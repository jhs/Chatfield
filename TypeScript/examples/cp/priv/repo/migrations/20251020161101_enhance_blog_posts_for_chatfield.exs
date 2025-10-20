defmodule Cp.Repo.Migrations.EnhanceBlogPostsForChatfield do
  use Ecto.Migration

  def change do
    alter table(:posts) do
      # Translation fields - stores Thai translations
      add :title_th, :string
      add :body_th, :text

      # Category - single selection from predefined options
      add :category, :string

      # Tags - set of unique strings (array in Postgres)
      add :tags, {:array, :string}, default: []
    end

    # Index for category filtering
    create index(:posts, [:category])

    # GIN index for tags array queries (efficient for "contains" queries)
    create index(:posts, [:tags], using: :gin)
  end
end
