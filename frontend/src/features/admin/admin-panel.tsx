"use client";

import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  createCuttingMachine,
  createEndpoint,
  createErpProfile,
  createMapping,
  createUser,
  fetchCurrentUser,
  fetchErpProfile,
  fetchErpProfiles,
  fetchEndpoints,
  fetchMappings,
  fetchCuttingMachines,
  fetchUsers,
} from "@/lib/api-client";
import type {
  CuttingMachineDto,
  ErpEndpointDto,
  ErpMappingDto,
  ErpProfileDto,
  UserDto,
} from "@/lib/types";

export function AdminPanel() {
  const [error, setError] = useState<string | null>(null);
  const [accessState, setAccessState] = useState<"loading" | "allowed" | "denied">("loading");

  const [erpProfiles, setErpProfiles] = useState<ErpProfileDto[]>([]);
  const [profileName, setProfileName] = useState("default");
  const [selectedProfileId, setSelectedProfileId] = useState("1");
  const [selectedProfile, setSelectedProfile] = useState<ErpProfileDto | null>(null);

  const [endpoints, setEndpoints] = useState<ErpEndpointDto[]>([]);
  const [endpointProfileId, setEndpointProfileId] = useState("1");
  const [endpointKey, setEndpointKey] = useState("material.search");
  const [endpointMethod, setEndpointMethod] = useState("GET");
  const [endpointPath, setEndpointPath] = useState("/materials/search");

  const [mappings, setMappings] = useState<ErpMappingDto[]>([]);
  const [mappingEndpointId, setMappingEndpointId] = useState("1");
  const [mappingAppField, setMappingAppField] = useState("material_reference");
  const [mappingErpField, setMappingErpField] = useState("material_no");
  const [mappingDirection, setMappingDirection] = useState<"app_to_erp" | "erp_to_app">("app_to_erp");

  const [cuttingMachines, setCuttingMachines] = useState<CuttingMachineDto[]>([]);
  const [machineName, setMachineName] = useState("Saege 1");
  const [machineCode, setMachineCode] = useState("S-01");
  const [machineKerf, setMachineKerf] = useState("3.0");

  const [users, setUsers] = useState<UserDto[]>([]);
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("demo-passwort");
  const [roleId, setRoleId] = useState("1");

  function handleError(err: unknown) {
    setError(err instanceof Error ? err.message : "Unbekannter Fehler");
  }

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
    checkAccess();
    return () => {
      active = false;
    };
  }, []);

  if (accessState === "loading") {
    return <p className="text-sm text-slate-700">Pruefe Berechtigung...</p>;
  }

  if (accessState === "denied") {
    return <p className="text-sm text-red-600">Kein Zugriff auf Admin-Bereich.</p>;
  }

  async function handleLoadProfiles() {
    setError(null);
    try {
      setErpProfiles(await fetchErpProfiles());
    } catch (err) {
      handleError(err);
    }
  }

  async function handleCreateProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const created = await createErpProfile({ name: profileName });
      setErpProfiles((current) => [...current, created]);
    } catch (err) {
      handleError(err);
    }
  }

  async function handleLoadProfileById(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      setSelectedProfile(await fetchErpProfile(Number(selectedProfileId)));
    } catch (err) {
      handleError(err);
    }
  }

  async function handleLoadEndpoints() {
    setError(null);
    try {
      setEndpoints(await fetchEndpoints());
    } catch (err) {
      handleError(err);
    }
  }

  async function handleCreateEndpoint(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const created = await createEndpoint({
        erp_profile_id: Number(endpointProfileId),
        functional_key: endpointKey,
        http_method: endpointMethod,
        path_template: endpointPath,
      });
      setEndpoints((current) => [...current, created]);
    } catch (err) {
      handleError(err);
    }
  }

  async function handleLoadMappings() {
    setError(null);
    try {
      setMappings(await fetchMappings());
    } catch (err) {
      handleError(err);
    }
  }

  async function handleCreateMapping(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const created = await createMapping({
        endpoint_id: Number(mappingEndpointId),
        app_field: mappingAppField,
        erp_field: mappingErpField,
        direction: mappingDirection,
      });
      setMappings((current) => [...current, created]);
    } catch (err) {
      handleError(err);
    }
  }

  async function handleLoadMachines() {
    setError(null);
    try {
      setCuttingMachines(await fetchCuttingMachines());
    } catch (err) {
      handleError(err);
    }
  }

  async function handleCreateMachine(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const created = await createCuttingMachine({
        machine_code: machineCode || null,
        name: machineName,
        kerf_mm: Number(machineKerf),
        is_active: true,
      });
      setCuttingMachines((current) => [...current, created]);
    } catch (err) {
      handleError(err);
    }
  }

  async function handleLoadUsers() {
    setError(null);
    try {
      setUsers(await fetchUsers());
    } catch (err) {
      handleError(err);
    }
  }

  async function handleCreateUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const created = await createUser({
        username,
        password,
        role_id: Number(roleId),
        is_active: true,
      });
      setUsers((current) => [...current, created]);
    } catch (err) {
      handleError(err);
    }
  }

  return (
    <div className="grid gap-6">
      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <section className="grid gap-3 rounded border border-slate-200 p-4">
        <h2 className="text-lg font-medium">ERP-Profile</h2>
        <div className="flex gap-2">
          <Button onClick={handleLoadProfiles}>Liste laden</Button>
        </div>
        <ul className="grid gap-1 text-sm">
          {erpProfiles.map((profile) => (
            <li key={profile.id}>
              #{profile.id} - {profile.name}
            </li>
          ))}
        </ul>
        <form className="grid gap-2" onSubmit={handleCreateProfile}>
          <Input value={profileName} onChange={(event) => setProfileName(event.target.value)} required />
          <Button type="submit">Profil anlegen</Button>
        </form>
        <form className="grid gap-2" onSubmit={handleLoadProfileById}>
          <Input
            type="number"
            min={1}
            value={selectedProfileId}
            onChange={(event) => setSelectedProfileId(event.target.value)}
            required
          />
          <Button type="submit">Profil laden (GET by ID)</Button>
        </form>
        {selectedProfile ? (
          <p className="text-sm">Ausgewaehlt: #{selectedProfile.id} - {selectedProfile.name}</p>
        ) : null}
      </section>

      <section className="grid gap-3 rounded border border-slate-200 p-4">
        <h2 className="text-lg font-medium">Endpoints</h2>
        <Button onClick={handleLoadEndpoints}>Liste laden</Button>
        <ul className="grid gap-1 text-sm">
          {endpoints.map((endpoint) => (
            <li key={endpoint.id}>
              #{endpoint.id} - {endpoint.functional_key} ({endpoint.http_method})
            </li>
          ))}
        </ul>
        <form className="grid gap-2" onSubmit={handleCreateEndpoint}>
          <Input
            type="number"
            min={1}
            value={endpointProfileId}
            onChange={(event) => setEndpointProfileId(event.target.value)}
            required
          />
          <Input value={endpointKey} onChange={(event) => setEndpointKey(event.target.value)} required />
          <Input value={endpointMethod} onChange={(event) => setEndpointMethod(event.target.value)} required />
          <Input value={endpointPath} onChange={(event) => setEndpointPath(event.target.value)} required />
          <Button type="submit">Endpoint anlegen</Button>
        </form>
      </section>

      <section className="grid gap-3 rounded border border-slate-200 p-4">
        <h2 className="text-lg font-medium">Feldmapping</h2>
        <Button onClick={handleLoadMappings}>Liste laden</Button>
        <ul className="grid gap-1 text-sm">
          {mappings.map((mapping) => (
            <li key={mapping.id}>
              #{mapping.id} - {mapping.direction}: {mapping.app_field} {"->"} {mapping.erp_field}
            </li>
          ))}
        </ul>
        <form className="grid gap-2" onSubmit={handleCreateMapping}>
          <Input
            type="number"
            min={1}
            value={mappingEndpointId}
            onChange={(event) => setMappingEndpointId(event.target.value)}
            required
          />
          <Input value={mappingAppField} onChange={(event) => setMappingAppField(event.target.value)} required />
          <Input value={mappingErpField} onChange={(event) => setMappingErpField(event.target.value)} required />
          <select
            className="h-10 rounded-md border border-slate-300 px-3 text-sm"
            value={mappingDirection}
            onChange={(event) => setMappingDirection(event.target.value as "app_to_erp" | "erp_to_app")}
          >
            <option value="app_to_erp">app_to_erp</option>
            <option value="erp_to_app">erp_to_app</option>
          </select>
          <Button type="submit">Mapping anlegen</Button>
        </form>
      </section>

      <section className="grid gap-3 rounded border border-slate-200 p-4">
        <h2 className="text-lg font-medium">Saegen</h2>
        <Button onClick={handleLoadMachines}>Liste laden</Button>
        <ul className="grid gap-1 text-sm">
          {cuttingMachines.map((machine) => (
            <li key={machine.id}>
              #{machine.id} - {machine.name} ({machine.kerf_mm ?? "-"} mm)
            </li>
          ))}
        </ul>
        <form className="grid gap-2" onSubmit={handleCreateMachine}>
          <Input value={machineCode} onChange={(event) => setMachineCode(event.target.value)} />
          <Input value={machineName} onChange={(event) => setMachineName(event.target.value)} required />
          <Input
            type="number"
            min={0}
            step="0.1"
            value={machineKerf}
            onChange={(event) => setMachineKerf(event.target.value)}
            required
          />
          <Button type="submit">Saege anlegen</Button>
        </form>
      </section>

      <section className="grid gap-3 rounded border border-slate-200 p-4">
        <h2 className="text-lg font-medium">Users</h2>
        <Button onClick={handleLoadUsers}>Liste laden</Button>
        <ul className="grid gap-1 text-sm">
          {users.map((user) => (
            <li key={user.id}>
              #{user.id} - {user.username} (Rolle {user.role_id})
            </li>
          ))}
        </ul>
        <form className="grid gap-2" onSubmit={handleCreateUser}>
          <Input value={username} onChange={(event) => setUsername(event.target.value)} required />
          <Input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
          <Input
            type="number"
            min={1}
            value={roleId}
            onChange={(event) => setRoleId(event.target.value)}
            required
          />
          <Button type="submit">User anlegen</Button>
        </form>
      </section>
    </div>
  );
}
