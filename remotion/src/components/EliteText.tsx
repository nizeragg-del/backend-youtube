import React from "react";
import { 
  useCurrentFrame, 
  useVideoConfig, 
  interpolate 
} from "remotion";
import { MotionSprings, maskReveal } from "../utils/motion";
import { montserrat, playfair } from "../fonts";

interface EliteTextProps {
  text: string;
  type?: "title" | "subtitle" | "caption";
  color?: string;
  delay?: number;
}

export const EliteText: React.FC<EliteTextProps> = ({ 
  text, 
  type = "title", 
  color,
  delay = 0 
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  const spr = MotionSprings.bouncy(frame - delay, fps);
  const reveal = maskReveal(frame, fps, delay);
  
  const isCaption = type === "caption";
  const fontSize = isCaption ? "110px" : type === "title" ? "120px" : "60px";
  const fontFamily = isCaption ? montserrat : playfair;
  
  const letterSpacing = isCaption ? "2px" : type === "title" 
    ? interpolate(frame - delay, [0, 60], [2, 12], { extrapolateRight: "clamp" }) 
    : "normal";

  return (
    <div style={{
      ...reveal,
      fontFamily,
      fontSize,
      fontWeight: 900,
      color: color || (isCaption ? "#FFD700" : "white"),
      textAlign: "center",
      textTransform: "uppercase",
      letterSpacing,
      textShadow: isCaption 
        ? "0 0 20px rgba(255, 215, 0, 0.5), 0 10px 40px rgba(0,0,0,0.8)" 
        : "0 10px 30px rgba(0,0,0,0.5)",
      padding: "0 60px",
      lineHeight: 1.1,
      opacity: spr,
      filter: isCaption ? "drop-shadow(0 0 10px rgba(255,215,0,0.3))" : "none"
    }}>
      {text}
    </div>
  );
};
