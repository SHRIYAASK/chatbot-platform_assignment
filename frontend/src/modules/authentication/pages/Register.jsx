import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import Button from "../../../shared/components/Button.jsx";
import Input from "../../../shared/components/Input.jsx";
import { useToast } from "../../../shared/hooks/useToast.jsx";
import { formatApiDetail } from "../../../shared/utils/formatApiDetail.js";
import { registerUser } from "../services/authService.js";
import { useAuth } from "../context/AuthContext.jsx";
import {
  PASSWORD_REQUIREMENTS,
  validateRegisterForm,
} from "../utils/validation.js";

export default function Register() {
  const { login, isAuthenticated } = useAuth();
  const { showError, showSuccess } = useToast();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: "" }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const result = validateRegisterForm(form);
    setErrors(result.errors);
    if (!result.isValid) {
      return;
    }

    setSubmitting(true);

    try {
      await registerUser(result.payload);
      await login({ email: result.payload.email, password: result.payload.password });
      showSuccess("Account created successfully.");
    } catch (error) {
      const message = formatApiDetail(
        error.response?.data?.detail,
        "Registration failed."
      );
      showError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[calc(100vh-73px)] max-w-md items-center px-4 py-10">
      <div className="w-full rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">Register</h1>
        <p className="mt-2 text-sm text-slate-600">
          Create an account to start building AI assistants.
        </p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <Input
            label="Full Name"
            id="name"
            name="name"
            value={form.name}
            onChange={handleChange}
            error={errors.name}
            required
          />
          <Input
            label="Email"
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            error={errors.email}
            required
          />
          <Input
            label="Password"
            id="password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            error={errors.password}
            required
          />
          <p className="text-xs text-slate-500">{PASSWORD_REQUIREMENTS}</p>
          <Input
            label="Confirm Password"
            id="confirm_password"
            name="confirm_password"
            type="password"
            value={form.confirm_password}
            onChange={handleChange}
            error={errors.confirm_password}
            required
          />
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? "Creating account..." : "Register"}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-600">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-brand-600 hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
