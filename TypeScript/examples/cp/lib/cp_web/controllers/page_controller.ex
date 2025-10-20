defmodule CpWeb.PageController do
  use CpWeb, :controller

  def home(conn, _params) do
    render(conn, :home)
  end
end
