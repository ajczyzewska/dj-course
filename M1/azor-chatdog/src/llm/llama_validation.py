from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
import os

class LlamaConfig(BaseModel):
    engine: Literal["LLAMA"] = Field(default="LLAMA")
    model_name: str = Field(..., description="Nazwa modelu Llama")
    llama_model_path: str = Field(..., description="Ścieżka do pliku modelu .gguf")
    llama_gpu_layers: int = Field(default=1, ge=-1, description="Liczba warstw GPU (-1 = wszystkie warstwy)")
    llama_context_size: int = Field(default=2048, ge=1, description="Rozmiar kontekstu")

    # Parametry generowania
    llama_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature (0.0-2.0) - wyższa = bardziej kreatywne")
    llama_top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Top P (0.0-1.0) - nucleus sampling")
    llama_top_k: int = Field(default=40, ge=0, description="Top K (0 = wyłączone) - liczba najlepszych tokenów do rozważenia")
    
    @validator('llama_model_path')
    def validate_model_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"Plik modelu nie istnieje: {v}")
        if not v.endswith('.gguf'):
            raise ValueError("Plik modelu musi mieć rozszerzenie .gguf")
        return v
