import { spring, Easing } from "remotion";

/**
 * Curvas de Easing Profissionais para Motion Design
 */
export const MotionEasings = {
  // Entrada clássica e suave
  easeOutCubic: Easing.out(Easing.cubic),
  // Entrada dramática com "back"
  backOut: Easing.out(Easing.back(1.7)),
  // Movimento de câmera cinematográfico
  slowSlow: Easing.inOut(Easing.quad),
  // Exponencial para flash de luz
  expoOut: Easing.out(Easing.exp),
};

/**
 * Presets de mola (Spring) para consistência visual
 */
export const MotionSprings = {
  // Para textos e legendas (Bouncy)
  bouncy: (frame: number, fps: number) => 
    spring({
      frame,
      fps,
      config: {
        damping: 12,
        stiffness: 100,
        mass: 0.8,
      },
    }),
  // Para elementos gráficos (Smooth)
  smooth: (frame: number, fps: number) => 
    spring({
      frame,
      fps,
      config: {
        damping: 20,
        stiffness: 80,
        mass: 1,
      },
    }),
  // Para transições rápidas (Snappy)
  snappy: (frame: number, fps: number) => 
    spring({
      frame,
      fps,
      config: {
        damping: 10,
        stiffness: 150,
        mass: 0.5,
      },
    }),
};

/**
 * Função para criar Mask Reveal (Texto subindo)
 */
export const maskReveal = (frame: number, fps: number, delay = 0) => {
  const spr = spring({
    frame: frame - delay,
    fps,
    config: { damping: 20 },
  });
  
  return {
    clipPath: `inset(0 0 ${100 - spr * 100}% 0)`,
    transform: `translateY(${(1 - spr) * 20}px)`,
  };
};
