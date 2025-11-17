import React, { ChangeEvent } from 'react';

interface LLMProviderSelectorProps {
  llmProviderMode: string;
  onLLMProviderChange: (event: ChangeEvent<HTMLSelectElement>) => void;
}

export default function LLMProviderSelector({ llmProviderMode, onLLMProviderChange }: LLMProviderSelectorProps) {
  return (
    <div className="form-group">
      <label htmlFor="llm_provider_mode" className="agent_question">
        LLM Provider Mode{" "}
      </label>
      <select 
        name="llm_provider_mode" 
        id="llm_provider_mode" 
        value={llmProviderMode} 
        onChange={onLLMProviderChange} 
        className="form-control-static"
        required
      >
        <option value="litellm">LiteLLM - Use online models via LiteLLM</option>
        <option value="ollama">Ollama - Use local models via Ollama</option>
      </select>
    </div>
  );
}

