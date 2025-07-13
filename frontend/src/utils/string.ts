export function toTitleCase(str: string) {
  return str.replace(
    /\w\S*/g,
    (text) => text.charAt(0).toUpperCase() + text.substring(1).toLowerCase()
  );
}

export function parseDecisionReason(str: string) {
  if (!str) {
    return null
  }

  const match = str.match(/Decision:\s*(\w+)\s+Reason:\s*(.+)/i);
  if (match) {
    return {
      decision:
        match[1].charAt(0).toUpperCase() + match[1].slice(1).toLowerCase(),
      reason: match[2].trim(),
    };
  }
  
  return null;
}
