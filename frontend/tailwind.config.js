/** @type {import('tailwindcss').Config} */
import { colors as defaultColors } from "tailwindcss/defaultTheme";
import { screens as defaultScreens } from "tailwindcss/defaultTheme";
import customColors from "./src/configs/colors.json";

export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ...defaultColors,
        ...customColors
      },
      fontFamily: {
        body: ["Helvetica", "Arial", "sans-serif"],
        header: ["Helvetica", "Arial", "sans-serif"],
      },
    },
    screens: {
      ...defaultScreens,
      ...{
        "theme-lg": "992px",
      },
    },
  },
  important: true,
  plugins: [],
  prefix: "tw-",
  corePlugins: {
    preflight: false,
  },
};
