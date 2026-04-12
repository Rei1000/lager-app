import { PageShell } from "@/components/shared/page-shell";
import { LoginForm } from "@/features/auth/login-form";

export default function LoginPage() {
  return (
    <PageShell title="Anmeldung">
      <LoginForm />
    </PageShell>
  );
}
