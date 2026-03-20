import React from "react";
import { Composition, getInputProps } from "remotion";
import { ShortsComp, ShortsProps } from "./ShortsComp";

export const RemotionRoot: React.FC = () => {
  const inputProps = (getInputProps() || {
    title: "Novo Vídeo",
    scriptText: "",
    syncData: [],
  }) as unknown as ShortsProps;

  // Calculando duração baseada no último timestamp
  const lastWord = inputProps?.syncData?.[inputProps.syncData.length - 1];
  const durationInSeconds = lastWord ? lastWord.end + 1 : 30;
  const durationInFrames = Math.max(30, Math.ceil(durationInSeconds * 30));

  const defaultProps: ShortsProps = {
    title: "Novo Vídeo",
    scriptText: "Exemplo de mensagem para teste.",
    syncData: [],
    audioUrl: ""
  };

  return (
    <>
      <Composition
        id="ShortsComp"
        component={ShortsComp as any}
        durationInFrames={durationInFrames}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={defaultProps}
      />
    </>
  );
};
