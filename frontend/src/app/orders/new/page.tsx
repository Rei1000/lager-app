import { redirect } from "next/navigation";

/** Frueher eigenstaendige Planungsseite; Planung liegt jetzt im Tab „Neuer Auftrag“ auf /orders. */
export default function NewOrderRedirectPage() {
  redirect("/orders");
}
