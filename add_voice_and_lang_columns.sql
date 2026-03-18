-- Adiciona as colunas necessárias para a Galeria de Narradores e Seleção de Idioma
ALTER TABLE user_configs 
ADD COLUMN IF NOT EXISTS voice_id TEXT DEFAULT 'tc_5f8d7b0de146f10007b8042f',
ADD COLUMN IF NOT EXISTS voice_language TEXT DEFAULT 'Português';
