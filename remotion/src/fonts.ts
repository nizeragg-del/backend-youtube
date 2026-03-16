import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";

// Carregamento centralizado para evitar múltiplas requisições de rede
export const { fontFamily: montserrat } = loadMontserrat(undefined, {
  subsets: ["latin"],
});

export const { fontFamily: playfair } = loadPlayfair(undefined, {
  subsets: ["latin"],
});
