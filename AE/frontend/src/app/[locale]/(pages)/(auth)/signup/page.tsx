import RegisterForm from "@/components/ui/auth/register-form";

export default function SignupPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 py-8 px-4">
      <div className="w-full max-w-md mx-auto">
        <RegisterForm />
      </div>
    </div>
  );
}