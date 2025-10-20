defmodule Cp.Blog.Post do
  use Ecto.Schema
  import Ecto.Changeset

  schema "posts" do
    field :title, :string
    field :body, :string
    field :title_th, :string
    field :body_th, :string
    field :category, :string
    field :tags, {:array, :string}

    timestamps(type: :utc_datetime)
  end

  @doc false
  def changeset(post, attrs) do
    post
    |> cast(attrs, [:title, :body, :title_th, :body_th, :category, :tags])
    |> validate_required([:title, :body])
  end
end
