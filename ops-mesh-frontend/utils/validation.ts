// utils/validation.ts
export function validateAppointmentInput(code: string, last: string) {
  if (!code?.trim() && !last?.trim()) return "Please enter your confirmation code and last name.";
  if (!code?.trim()) return "Please enter your confirmation code.";
  if (!last?.trim()) return "Please enter your last name.";
  return null;
}

export function decideNextAfterInvalid(attempts: number): "retry" | "walkin" {
  return attempts >= 2 ? "walkin" : "retry";
}
