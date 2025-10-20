defmodule CpWeb.ThermostatLive do
  use CpWeb, :live_view

  def render(assigns) do
    ~H"""
    Current temperature: {@temperature}°F
    <br>
    <button phx-click="inc_temperature">+</button>
    <br>
    <button phx-click="dec_temperature">-</button>
    """
  end

  def mount(_params, _session, socket) do
    temperature = 70 # Let's assume a fixed temperature for now
    age = 25
    # {:ok, assign(socket, :temperature, temperature)}
    {:ok, assign(socket, temperature: temperature, age: age)}
  end

  def handle_event("inc_temperature", _params, socket) do
    {:noreply, update(socket, :temperature, &(&1 + 1))}
  end

  def handle_event("dec_temperature", _params, socket) do
    {:noreply, update(socket, :temperature, &(&1 - 2))}
  end
end
