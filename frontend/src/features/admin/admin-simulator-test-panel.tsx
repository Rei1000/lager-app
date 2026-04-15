"use client";

import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  ApiClientError,
  fetchCurrentUser,
  fetchSimulatorMaterialStock,
  getMaterialByArticleNumber,
  searchSimulatorMaterials,
} from "@/lib/api-client";
import type { MaterialLookupDto, SimulatorMaterialSearchDto } from "@/lib/types";

const MAIN_GROUP_OPTIONS = ["100", "200", "300", "400", "410", "420", "430", "440"] as const;
const MATERIAL_OPTIONS = ["FE", "AL", "CU", "VA", "MS"] as const;
const DIMENSION_OPTIONS = ["010", "012", "025", "050", "100"] as const;

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
  const [activeTab, setActiveTab] = useState<"artikel" | "erp-benutzer">("artikel");
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
  const [detailErrorMessage, setDetailErrorMessage] = useState<string | null>(null);
  const [detailHttpStatus, setDetailHttpStatus] = useState<number | null>(null);

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

  function matchesFilters(item: SimulatorMaterialSearchDto): boolean {
    const [groupCode, materialCode, dimensionCode] = item.material_no.split("-");
    if (mainGroupFilter && groupCode !== mainGroupFilter) {
      return false;
    }
    if (materialFilter && materialCode !== materialFilter) {
      return false;
    }
    if (dimensionFilter && dimensionCode !== dimensionFilter) {
      return false;
    }
    return true;
  }

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setHasSearched(true);
    setSearchLoading(true);
    setSearchError(null);
    setSearchStatusText(null);
    setSearchResults([]);

    try {
      const rawResults = await searchSimulatorMaterials(searchQuery.trim());
      const filteredResults = rawResults.filter(matchesFilters);

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
      setDetailHttpStatus(null);
      setDetailErrorMessage("Bitte Artikelnummer eingeben");
      return;
    }

    setDetailLoading(true);
    setMaterial(null);
    setDetailHttpStatus(null);
    setDetailErrorMessage(null);
    try {
      const response = await getMaterialByArticleNumber(normalized);
      setMaterial(response);
    } catch (error) {
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
      setDetailLoading(false);
    }
  }

  async function handleLoadMaterial(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadMaterialDetails(articleNumber);
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
              <p title="Verfuegbarer Bestand in Meter">Lagerbestand (Meter): {material.erp_stock_m ?? "-"}</p>
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
      </section>

      {activeTab === "artikel" ? renderArtikelTab() : renderErpUsersTab()}
    </div>
  );
}
