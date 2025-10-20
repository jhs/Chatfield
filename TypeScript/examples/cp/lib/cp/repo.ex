defmodule Cp.Repo do
  use Ecto.Repo,
    otp_app: :cp,
    adapter: Ecto.Adapters.Postgres
end
