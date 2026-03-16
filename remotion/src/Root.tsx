import React from "react";
import { Composition, getInputProps } from "remotion";
import { ShortsComp, ShortsProps } from "./ShortsComp";

export const RemotionRoot: React.FC = () => {
  const inputProps = (getInputProps() || {}) as ShortsProps;

  // Calculando duração baseada no último timestamp
  const lastWord = inputProps?.syncData?.[inputProps.syncData.length - 1];
  const durationInSeconds = lastWord ? lastWord.end + 1 : 30;
  const durationInFrames = Math.max(30, Math.ceil(durationInSeconds * 30));

  return (
    <>
      <Composition
        id="ShortsComp"
        component={ShortsComp}
        durationInFrames={durationInFrames}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "Mensagem do Dia",
          scriptText: "Exemplo de mensagem para teste.",
          syncData: [],
          audioUrl: ""
        } as ShortsProps}
      />
    </>
  );
};
