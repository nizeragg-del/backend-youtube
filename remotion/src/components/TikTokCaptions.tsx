import React, { useMemo } from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  spring,
} from "remotion";
import { makeTransform, scale, translateY } from "@remotion/animation-utils";
import { fitText } from "@remotion/layout-utils";
import { montserrat } from "../fonts";
import { WordSync } from "../ShortsComp";

interface TikTokCaptionsProps {
  syncData: WordSync[];
  wordsPerPhrase?: number;
}

const DESIRED_FONT_SIZE = 120;
const HIGHLIGHT_COLOR = "#39E508"; // TikTok Green

export const TikTokCaptions: React.FC<TikTokCaptionsProps> = ({
  syncData,
  wordsPerPhrase = 3,
}) => {
  const frame = useCurrentFrame();
  const { width, fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Group words into "pages" (phrases)
  const pages = useMemo(() => {
    const arr = [];
    for (let i = 0; i < syncData.length; i += wordsPerPhrase) {
      const chunk = syncData.slice(i, i + wordsPerPhrase);
      arr.push({
        tokens: chunk,
        text: chunk.map((w) => w.word).join(" "),
        start: chunk[0].start,
        end: chunk[chunk.length - 1].end + 0.5, // Buffer
      });
    }
    return arr;
  }, [syncData, wordsPerPhrase]);

  const activePage = pages.find(
    (p) => currentTime >= p.start && currentTime <= p.end
  );

  if (!activePage) return null;

  // Animation for the entire page entry
  const pageFrame = Math.max(0, frame - activePage.start * fps);
  const enterProgress = spring({
    frame: pageFrame,
    fps,
    config: { damping: 200 },
  });

  const fittedText = fitText({
    fontFamily: montserrat,
    text: activePage.text.toUpperCase(),
    withinWidth: width * 0.9,
  });

  const fontSize = Math.min(DESIRED_FONT_SIZE, fittedText.fontSize);

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        top: "auto",
        bottom: 350,
        height: 200,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          fontSize,
          color: "white",
          WebkitTextStroke: "15px black",
          paintOrder: "stroke",
          transform: makeTransform([
            scale(interpolate(enterProgress, [0, 1], [0.8, 1])),
            translateY(interpolate(enterProgress, [0, 1], [50, 0])),
          ]),
          fontFamily: montserrat,
          fontWeight: 900,
          textTransform: "uppercase",
          textAlign: "center",
          padding: "0 40px",
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: "0 15px",
        }}
      >
        {activePage.tokens.map((t, i) => {
          const active = currentTime >= t.start && currentTime <= t.end;

          return (
            <span
              key={`${t.word}-${i}`}
              style={{
                color: active ? HIGHLIGHT_COLOR : "white",
                display: "inline-block",
              }}
            >
              {t.word}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
