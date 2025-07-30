import LoginForm from "@/components/ui/auth/login-form";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 py-8 px-4">
      <div className="w-full max-w-md mx-auto">
        <LoginForm />
      </div>
    </div>
  );
}
