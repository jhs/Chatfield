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
    attrs = process_tags(attrs)

    post
    |> cast(attrs, [:title, :body, :title_th, :body_th, :category, :tags])
    |> validate_required([:title, :body])
  end

  # Convert comma-separated string to array for tags field
  defp process_tags(%{"tags" => tags} = attrs) when is_binary(tags) do
    tags_array =
      tags
      |> String.split(",")
      |> Enum.map(&String.trim/1)
      |> Enum.reject(&(&1 == ""))

    Map.put(attrs, "tags", tags_array)
  end

  defp process_tags(attrs), do: attrs
end
