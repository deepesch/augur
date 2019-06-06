export default function debounce(func: () => void, wait = 250): () => void {
  let timeout;
  return (...args: any) => {
    const later = () => {
      timeout = null;
      func.apply(null, args);
    };

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
