import { redirect } from "next/navigation";

/**
 * 根路徑重定向到儀表板
 */
export default function HomePage() {
  redirect("/dashboard");
}
