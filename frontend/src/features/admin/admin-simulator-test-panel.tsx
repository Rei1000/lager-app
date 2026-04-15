"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  ApiClientError,
  fetchCurrentUser,
  fetchSimulatorMaterialAvailability,
  fetchSimulatorOpenOrders,
  fetchSimulatorMaterialStock,
  getMaterialByArticleNumber,
  searchSimulatorMaterials,
} from "@/lib/api-client";
import type {
  MaterialLookupDto,
  SimulatorMaterialAvailabilityDto,
  SimulatorMaterialSearchDto,
  SimulatorOpenOrderDto,
} from "@/lib/types";
import {
  DIMENSION_OPTIONS,
  MAIN_GROUP_OPTIONS,
  MATERIAL_OPTIONS,
  matchesSimulatorMaterialFilters,
} from "@/features/orders/simulator-material-search-constants";

type SearchResultRow = {
  article_number: string;
  description: string;
  stock_m: number | null;
};

type SimulatorErpUser = {
  username: string;
  external_id: string;
  role: "admin" | "leitung" | "lager";
};

const SIMULATOR_ERP_USERS: SimulatorErpUser[] = [
  { username: "sage_admin", external_id: "ERP-SAGE-USER-ADMIN-001", role: "admin" },
  { username: "sage_leitung", external_id: "ERP-SAGE-USER-LEITUNG-001", role: "leitung" },
  { username: "sage_lager", external_id: "ERP-SAGE-USER-LAGER-001", role: "lager" },
];

export function AdminSimulatorTestPanel() {
  const [accessState, setAccessState] = useState<"loading" | "allowed" | "denied">("loading");
  const [activeTab, setActiveTab] = useState<"artikel" | "erp-benutzer" | "auftraege">("artikel");
  const [expandedUser, setExpandedUser] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [mainGroupFilter, setMainGroupFilter] = useState("");
  const [materialFilter, setMaterialFilter] = useState("");
  const [dimensionFilter, setDimensionFilter] = useState("");
  const [searchLoading, setSearchLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResultRow[]>([]);
  const [searchStatusText, setSearchStatusText] = useState<string | null>(null);

  const [articleNumber, setArticleNumber] = useState("100-FE-010");
  const [detailLoading, setDetailLoading] = useState(false);
  const [material, setMaterial] = useState<MaterialLookupDto | null>(null);
  const [materialAvailability, setMaterialAvailability] = useState<SimulatorMaterialAvailabilityDto | null>(null);
  const [detailErrorMessage, setDetailErrorMessage] = useState<string | null>(null);
  const [detailHttpStatus, setDetailHttpStatus] = useState<number | null>(null);

  const [ordersLoading, setOrdersLoading] = useState(false);
  const [ordersLoaded, setOrdersLoaded] = useState(false);
  const [ordersError, setOrdersError] = useState<string | null>(null);
  const [openOrders, setOpenOrders] = useState<SimulatorOpenOrderDto[]>([]);
  const [orderMaterialFilter, setOrderMaterialFilter] = useState("");
  const [orderStatusFilter, setOrderStatusFilter] = useState("");

  /** Verhindert, dass eine ältere Detail-Ladung eine neuere überschreibt (z. B. schnelle Klicks in der Trefferliste). */
  const detailLoadGeneration = useRef(0);

  useEffect(() => {
    let active = true;
    async function checkAccess() {
      try {
        const currentUser = await fetchCurrentUser();
        if (!active) {
          return;
        }
        setAccessState(currentUser.role_code === "admin" ? "allowed" : "denied");
      } catch {
        if (active) {
          setAccessState("denied");
        }
      }
    }
    void checkAccess();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (activeTab !== "auftraege" || ordersLoaded) {
      return;
    }
    void loadOpenOrders();
  }, [activeTab, ordersLoaded]);

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setHasSearched(true);
    setSearchLoading(true);
    setSearchError(null);
    setSearchStatusText(null);
    setSearchResults([]);

    try {
      const rawResults = await searchSimulatorMaterials(searchQuery.trim());
      const filteredResults = rawResults.filter((item) =>
        matchesSimulatorMaterialFilters(item, {
          mainGroup: mainGroupFilter,
          material: materialFilter,
          dimension: dimensionFilter,
        })
      );

      if (filteredResults.length === 0) {
        setSearchStatusText("Keine Treffer");
        return;
      }

      const rows = await Promise.all(
        filteredResults.map(async (item) => {
          try {
            const stockPayload = await fetchSimulatorMaterialStock(item.material_no);
            return {
              article_number: item.material_no,
              description: item.description,
              stock_m: stockPayload.stock_m,
            };
          } catch {
            return {
              article_number: item.material_no,
              description: item.description,
              stock_m: null,
            };
          }
        })
      );
      setSearchResults(rows);
      setSearchStatusText(`${rows.length} Treffer`);
    } catch {
      setSearchError("Fehler beim Laden");
    } finally {
      setSearchLoading(false);
    }
  }

  async function loadMaterialDetails(targetArticleNumber: string) {
    const normalized = targetArticleNumber.trim();
    if (!normalized) {
      setMaterial(null);
      setMaterialAvailability(null);
      setDetailHttpStatus(null);
      setDetailErrorMessage("Bitte Artikelnummer eingeben");
      return;
    }

    const generation = ++detailLoadGeneration.current;

    setDetailLoading(true);
    setMaterial(null);
    setMaterialAvailability(null);
    setDetailHttpStatus(null);
    setDetailErrorMessage(null);
    try {
      const materialResponse = await getMaterialByArticleNumber(normalized);
      if (generation !== detailLoadGeneration.current) {
        return;
      }
      const canonicalArticleNo = materialResponse.article_number.trim();
      const availabilityResponse = await fetchSimulatorMaterialAvailability(canonicalArticleNo);
      if (generation !== detailLoadGeneration.current) {
        return;
      }
      setMaterial(materialResponse);
      setMaterialAvailability(availabilityResponse);
    } catch (error) {
      if (generation !== detailLoadGeneration.current) {
        return;
      }
      if (error instanceof ApiClientError) {
        setDetailHttpStatus(error.status);
        if (error.status === 404) {
          setDetailErrorMessage("Artikel nicht gefunden");
        } else {
          setDetailErrorMessage("Fehler beim Laden");
        }
      } else {
        setDetailErrorMessage("Fehler beim Laden");
      }
    } finally {
      if (generation === detailLoadGeneration.current) {
        setDetailLoading(false);
      }
    }
  }

  async function handleLoadMaterial(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadMaterialDetails(articleNumber);
  }

  async function loadOpenOrders() {
    setOrdersLoading(true);
    setOrdersError(null);
    try {
      const response = await fetchSimulatorOpenOrders();
      setOpenOrders(response);
      setOrdersLoaded(true);
    } catch {
      setOrdersError("Fehler beim Laden");
    } finally {
      setOrdersLoading(false);
    }
  }

  if (accessState === "loading") {
    return <p className="text-sm text-slate-700">Pruefe Berechtigung...</p>;
  }

  if (accessState === "denied") {
    return <p className="text-sm text-red-600">Kein Zugriff auf Admin-Bereich.</p>;
  }

  function renderArtikelTab() {
    return (
      <>
        <p className="rounded border border-slate-200 bg-slate-50 p-3 text-slate-700">
          Hier koennen Artikel aus dem Simulator gesucht und geprueft werden. Sie koennen entweder
          direkt eine Artikelnummer eingeben oder nach Material, Kategorie und Dimension filtern.
        </p>

        <section className="grid gap-3 rounded border border-slate-200 p-3">
          <h2 className="font-medium">Suche und Filter</h2>
          <form className="grid gap-2" onSubmit={handleSearch}>
            <label className="grid gap-1">
              Suche (Artikelnummer oder Beschreibung)
              <Input
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="z. B. stahl, profil oder 420"
              />
            </label>
            <div className="grid gap-2 sm:grid-cols-3">
              <label className="grid gap-1" title="Materialgruppe, z. B. 400 = Profilmaterial">
                Hauptgruppe
                <select
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  value={mainGroupFilter}
                  onChange={(event) => setMainGroupFilter(event.target.value)}
                >
                  <option value="">Alle</option>
                  {MAIN_GROUP_OPTIONS.map((group) => (
                    <option key={group} value={group}>
                      {group}
                    </option>
                  ))}
                </select>
              </label>
              <label className="grid gap-1" title="Werkstoff, z. B. FE = Stahl, AL = Aluminium">
                Material
                <select
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  value={materialFilter}
                  onChange={(event) => setMaterialFilter(event.target.value)}
                >
                  <option value="">Alle</option>
                  {MATERIAL_OPTIONS.map((materialCode) => (
                    <option key={materialCode} value={materialCode}>
                      {materialCode}
                    </option>
                  ))}
                </select>
              </label>
              <label className="grid gap-1" title="Mass in mm, z. B. 025 = 25 mm">
                Dimension
                <select
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  value={dimensionFilter}
                  onChange={(event) => setDimensionFilter(event.target.value)}
                >
                  <option value="">Alle</option>
                  {DIMENSION_OPTIONS.map((dimensionCode) => (
                    <option key={dimensionCode} value={dimensionCode}>
                      {dimensionCode}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <Button className="w-full sm:w-auto" type="submit" disabled={searchLoading}>
              Suche ausfuehren
            </Button>
          </form>
          {searchLoading ? <p>loading...</p> : null}
          {searchError ? <p className="text-red-600">{searchError}</p> : null}
          {searchStatusText ? <p className="text-slate-700">{searchStatusText}</p> : null}
        </section>

        <section className="grid gap-2 rounded border border-slate-200 p-3">
          <h2 className="font-medium">Trefferliste</h2>
          {!hasSearched ? (
            <p className="text-slate-600">Noch keine Suche ausgefuehrt</p>
          ) : searchResults.length === 0 ? (
            <p className="text-slate-600">Keine Treffer</p>
          ) : (
            <ul className="grid gap-2">
              {searchResults.map((item) => (
                <li key={item.article_number} className="grid gap-1 rounded border border-slate-200 p-2">
                  <p title="Eindeutige Kennung nach Schema CCC-MM-DDD">
                    Artikelnummer: {item.article_number}
                  </p>
                  <p>Beschreibung: {item.description}</p>
                  <p title="Verfuegbarer Bestand in Meter">
                    Lagerbestand (Meter): {item.stock_m ?? "-"}
                  </p>
                  <Button
                    className="w-full sm:w-auto"
                    onClick={() => {
                      setArticleNumber(item.article_number);
                      void loadMaterialDetails(item.article_number);
                    }}
                  >
                    Details laden
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="grid gap-2 rounded border border-slate-200 p-3">
          <h2 className="font-medium">Direkter Detailtest per Artikelnummer</h2>
          <form className="grid gap-2" onSubmit={handleLoadMaterial}>
            <label className="grid gap-1" title="Eindeutige Kennung nach Schema CCC-MM-DDD">
              Artikelnummer
              <Input
                value={articleNumber}
                onChange={(event) => setArticleNumber(event.target.value)}
                placeholder="z. B. 100-FE-010"
              />
            </label>
            <Button className="w-full sm:w-auto" type="submit" disabled={detailLoading}>
              Artikel laden
            </Button>
          </form>
          {detailLoading ? <p>loading...</p> : null}
          {detailErrorMessage ? <p className="text-red-600">{detailErrorMessage}</p> : null}
          {detailHttpStatus !== null ? <p className="text-slate-600">HTTP-Status: {detailHttpStatus}</p> : null}
        </section>

        <section className="grid gap-1 rounded border border-slate-200 p-3">
          <h2 className="font-medium">Detailanzeige</h2>
          {material ? (
            <>
              <p title="Eindeutige Kennung nach Schema CCC-MM-DDD">
                Artikelnummer: {material.article_number}
              </p>
              <p>Beschreibung: {material.name}</p>
              <p title="Physischer Lagerbestand in Meter">
                Bestand (Meter): {materialAvailability?.stock_m ?? material.erp_stock_m ?? "-"}
              </p>
              <p title="Summe offener Materialbedarfe aus noch nicht fertiggemeldeten Auftraegen">
                In Pipeline (Meter): {materialAvailability?.in_pipeline_m ?? "-"}
              </p>
              <p title="Bestand abzueglich offener Bedarfe">
                Verfuegbar (Meter): {materialAvailability?.available_m ?? "-"}
              </p>
              <div className="pt-2">
                <p className="font-medium" title="Offener Bedarf, der Material fuer laufende oder geplante Fertigung bindet">
                  Offene zugehoerige Auftraege
                </p>
                {materialAvailability?.open_orders.length ? (
                  <ul className="grid gap-1 pt-1">
                    {materialAvailability.open_orders.map((order) => (
                      <li key={order.order_no} className="rounded border border-slate-200 p-2">
                        <p>Auftragsnummer: {order.order_no}</p>
                        <p>Benoetigt (Meter): {order.required_m}</p>
                        <p>Status: {order.status}</p>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-600">Keine offenen Auftraege fuer dieses Material</p>
                )}
              </div>
            </>
          ) : (
            <p className="text-slate-600">Noch kein Detail geladen</p>
          )}
        </section>
      </>
    );
  }

  function renderErpUsersTab() {
    return (
      <section className="grid gap-3 rounded border border-slate-200 p-3">
        <p className="rounded border border-slate-200 bg-slate-50 p-3 text-slate-700">
          Diese Benutzer stammen aus dem Sage-Simulator und koennen fuer den ERP-Login verwendet
          werden.
        </p>
        <h2 className="font-medium">ERP-Benutzer</h2>
        <ul className="grid gap-2">
          {SIMULATOR_ERP_USERS.map((user) => {
            const isExpanded = expandedUser === user.username;
            return (
              <li key={user.username} className="rounded border border-slate-200 p-3">
                <p title="Benutzername fuer ERP-Login im Simulator">{user.username}</p>
                {isExpanded ? (
                  <div className="pt-1 text-slate-700">
                    <p title="Eindeutige ERP-Benutzer-ID im Simulator">ID: {user.external_id}</p>
                    <p title="Bestimmt die Berechtigungen im System (admin, leitung, lager)">
                      Rolle: {user.role}
                    </p>
                  </div>
                ) : null}
                <Button
                  className="mt-2 w-full sm:w-auto"
                  onClick={() => setExpandedUser(isExpanded ? null : user.username)}
                >
                  Daten anzeigen
                </Button>
              </li>
            );
          })}
        </ul>
      </section>
    );
  }

  function renderOrdersTab() {
    const filteredOpenOrders = openOrders.filter((order) => {
      if (orderMaterialFilter.trim() && !order.material_no.includes(orderMaterialFilter.trim())) {
        return false;
      }
      if (orderStatusFilter.trim() && order.status !== orderStatusFilter.trim()) {
        return false;
      }
      return true;
    });

    return (
      <section className="grid gap-3 rounded border border-slate-200 p-3">
        <p className="rounded border border-slate-200 bg-slate-50 p-3 text-slate-700">
          Hier sehen Sie offene Simulator-Auftraege und deren Materialbedarf.
        </p>
        <h2 className="font-medium">Auftraege</h2>
        <div className="grid gap-2 sm:grid-cols-3">
          <label className="grid gap-1">
            Materialnummer-Filter
            <Input
              value={orderMaterialFilter}
              onChange={(event) => setOrderMaterialFilter(event.target.value)}
              placeholder="z. B. 420-VA-012"
            />
          </label>
          <label className="grid gap-1">
            Status-Filter
            <Input
              value={orderStatusFilter}
              onChange={(event) => setOrderStatusFilter(event.target.value)}
              placeholder="z. B. open"
            />
          </label>
          <div className="flex items-end">
            <Button className="w-full sm:w-auto" onClick={() => void loadOpenOrders()}>
              Auftraege neu laden
            </Button>
          </div>
        </div>
        {ordersLoading ? <p>loading...</p> : null}
        {ordersError ? <p className="text-red-600">{ordersError}</p> : null}
        {!ordersLoading && !ordersError && filteredOpenOrders.length === 0 ? (
          <p className="text-slate-600">Keine offenen Auftraege gefunden</p>
        ) : null}
        {!ordersLoading && !ordersError && filteredOpenOrders.length > 0 ? (
          <ul className="grid gap-2">
            {filteredOpenOrders.map((order) => (
              <li key={order.order_no} className="rounded border border-slate-200 p-2">
                <p title="Offener Bedarf, der Material fuer laufende oder geplante Fertigung bindet">
                  Auftragsnummer: {order.order_no}
                </p>
                <p>Materialnummer: {order.material_no}</p>
                <p>Materialbeschreibung: {order.material_description}</p>
                <p>Benoetigte Meter: {order.required_m}</p>
                <p>Status: {order.status}</p>
              </li>
            ))}
          </ul>
        ) : null}
      </section>
    );
  }

  return (
    <div className="grid gap-4 text-sm">
      <section className="flex flex-wrap gap-2">
        <Button
          className={`w-full sm:w-auto ${
            activeTab === "artikel" ? "" : "bg-white text-slate-900 ring-1 ring-slate-300 hover:bg-slate-100"
          }`}
          onClick={() => setActiveTab("artikel")}
        >
          Artikel
        </Button>
        <Button
          className={`w-full sm:w-auto ${
            activeTab === "erp-benutzer"
              ? ""
              : "bg-white text-slate-900 ring-1 ring-slate-300 hover:bg-slate-100"
          }`}
          onClick={() => setActiveTab("erp-benutzer")}
        >
          ERP-Benutzer
        </Button>
        <Button
          className={`w-full sm:w-auto ${
            activeTab === "auftraege"
              ? ""
              : "bg-white text-slate-900 ring-1 ring-slate-300 hover:bg-slate-100"
          }`}
          onClick={() => setActiveTab("auftraege")}
        >
          Auftraege
        </Button>
      </section>

      {activeTab === "artikel" ? renderArtikelTab() : null}
      {activeTab === "erp-benutzer" ? renderErpUsersTab() : null}
      {activeTab === "auftraege" ? renderOrdersTab() : null}
    </div>
  );
}
