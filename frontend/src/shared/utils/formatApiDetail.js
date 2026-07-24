function cleanValidationMessage(message) {
  if (typeof message !== "string") {
    return "Validation failed.";
  }
  return message.replace(/^Value error,\s*/i, "");
}

export function formatApiDetail(detail, fallback = "Request failed.") {
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item.loc)
          ? item.loc.filter((part) => part !== "body").join(".")
          : "";
        const message = cleanValidationMessage(item.msg);
        return field ? `${field}: ${message}` : message;
      })
      .join(" ");
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (detail && typeof detail === "object" && detail.message) {
    return detail.message;
  }

  return fallback;
}
