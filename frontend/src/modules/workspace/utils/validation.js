export function validateProjectForm(form) {
  const title = form.title.trim();
  const description = form.description.trim();
  const errors = {};

  if (!title) {
    errors.title = "Project title is required.";
  } else if (title.length < 3) {
    errors.title = "Project title must be at least 3 characters.";
  } else if (title.length > 50) {
    errors.title = "Project title must not exceed 50 characters.";
  }

  if (!description) {
    errors.description = "Project description is required.";
  } else if (description.length < 10) {
    errors.description = "Project description must be at least 10 characters.";
  } else if (description.length > 500) {
    errors.description = "Project description must not exceed 500 characters.";
  }

  return {
    errors,
    isValid: Object.keys(errors).length === 0,
    payload: {
      title,
      description,
    },
  };
}
