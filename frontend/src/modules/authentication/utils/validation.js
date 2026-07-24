const NAME_PATTERN = /^[A-Za-z\s]+$/;
const PASSWORD_UPPERCASE = /[A-Z]/;
const PASSWORD_LOWERCASE = /[a-z]/;
const PASSWORD_DIGIT = /\d/;
const PASSWORD_SPECIAL = /[!@#$%^&*(),.?":{}|<>_\-+=[\]\\\/;'~]/;

export function validateRegisterForm(form) {
  const name = form.name.trim();
  const email = form.email.trim().toLowerCase();
  const { password, confirm_password: confirmPassword } = form;
  const errors = {};

  if (!name) {
    errors.name = "Full name is required.";
  } else if (name.length < 3) {
    errors.name = "Full name must be at least 3 characters.";
  } else if (name.length > 50) {
    errors.name = "Full name must not exceed 50 characters.";
  } else if (!NAME_PATTERN.test(name)) {
    errors.name = "Full name must contain only letters and spaces.";
  }

  if (!email) {
    errors.email = "Email is required.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = "Enter a valid email address.";
  }

  if (!password) {
    errors.password = "Password is required.";
  } else if (password.length < 8) {
    errors.password = "Password must be at least 8 characters.";
  } else if (password.length > 64) {
    errors.password = "Password must not exceed 64 characters.";
  } else if (
    !PASSWORD_UPPERCASE.test(password) ||
    !PASSWORD_LOWERCASE.test(password) ||
    !PASSWORD_DIGIT.test(password) ||
    !PASSWORD_SPECIAL.test(password)
  ) {
    errors.password =
      "Password must include uppercase, lowercase, a number, and a special character.";
  }

  if (!confirmPassword) {
    errors.confirm_password = "Please confirm your password.";
  } else if (password !== confirmPassword) {
    errors.confirm_password = "Passwords do not match.";
  }

  return {
    errors,
    isValid: Object.keys(errors).length === 0,
    payload: {
      name,
      email,
      password,
      confirm_password: confirmPassword,
    },
  };
}

export const PASSWORD_REQUIREMENTS =
  "At least 8 characters with uppercase, lowercase, a number, and a special character.";
