defmodule CpWeb.PostLive.Form do
  use CpWeb, :live_view

  alias Cp.Blog
  alias Cp.Blog.Post

  @impl true
  def render(assigns) do
    ~H"""
    <Layouts.app flash={@flash}>
      <.header>
        {@page_title}
        <:subtitle>Use this form to manage post records in your database.</:subtitle>
      </.header>

      <.form for={@form} id="post-form" phx-change="validate" phx-submit="save">
        <.input field={@form[:title]} type="text" label="Title" />
        <.input field={@form[:title_th]} type="text" label="Title (Thai)" />
        <.input field={@form[:body]} type="textarea" label="Body" />
        <.input field={@form[:body_th]} type="textarea" label="Body (Thai)" />
        <.input field={@form[:category]} type="select" label="Category"
                options={["Technology", "Design", "Business", "Personal"]} />
        <.input field={@form[:tags]} type="text" label="Tags"
                placeholder="Comma-separated tags (e.g., elixir, phoenix, web)" />
        <footer>
          <.button phx-disable-with="Saving..." variant="primary">Save Post</.button>
          <.button navigate={return_path(@return_to, @post)}>Cancel</.button>
        </footer>
      </.form>
    </Layouts.app>
    """
  end

  @impl true
  def mount(params, _session, socket) do
    {:ok,
     socket
     |> assign(:return_to, return_to(params["return_to"]))
     |> apply_action(socket.assigns.live_action, params)}
  end

  defp return_to("show"), do: "show"
  defp return_to(_), do: "index"

  defp apply_action(socket, :edit, %{"id" => id}) do
    post = Blog.get_post!(id)
    post = prepare_post_for_form(post)

    socket
    |> assign(:page_title, "Edit Article")
    |> assign(:post, post)
    |> assign(:form, to_form(Blog.change_post(post)))
  end

  defp apply_action(socket, :new, _params) do
    post = %Post{}

    socket
    |> assign(:page_title, "New Article")
    |> assign(:post, post)
    |> assign(:form, to_form(Blog.change_post(post)))
  end

  # Convert tags array to comma-separated string for form display
  defp prepare_post_for_form(%Post{tags: tags} = post) when is_list(tags) do
    %{post | tags: Enum.join(tags, ", ")}
  end

  defp prepare_post_for_form(post), do: post

  @impl true
  def handle_event("validate", %{"post" => post_params}, socket) do
    changeset = Blog.change_post(socket.assigns.post, post_params)
    {:noreply, assign(socket, form: to_form(changeset, action: :validate))}
  end

  def handle_event("save", %{"post" => post_params}, socket) do
    save_post(socket, socket.assigns.live_action, post_params)
  end

  defp save_post(socket, :edit, post_params) do
    case Blog.update_post(socket.assigns.post, post_params) do
      {:ok, post} ->
        {:noreply,
         socket
         |> put_flash(:info, "Post updated successfully")
         |> push_navigate(to: return_path(socket.assigns.return_to, post))}

      {:error, %Ecto.Changeset{} = changeset} ->
        {:noreply, assign(socket, form: to_form(changeset))}
    end
  end

  defp save_post(socket, :new, post_params) do
    case Blog.create_post(post_params) do
      {:ok, post} ->
        {:noreply,
         socket
         |> put_flash(:info, "Post created successfully")
         |> push_navigate(to: return_path(socket.assigns.return_to, post))}

      {:error, %Ecto.Changeset{} = changeset} ->
        {:noreply, assign(socket, form: to_form(changeset))}
    end
  end

  defp return_path("index", _post), do: ~p"/articles"
  defp return_path("show", post), do: ~p"/articles/#{post}"
end
