import flet as ft
import io
import re
import bcrypt
from datetime import datetime
import cloudinary.uploader as uploader

# Use direct imports for desktop application
from connection import supabase
from pipeline import generate_image

# --- Global State ---
current_user = None # Will store the user's data as a dict

# --- UI Constants & Theming ---
MAX_CONTENT_WIDTH = 800

# UPDATED: Changed to a true dark theme
DARK_THEME = {
    "background": "#121212",  # Very dark gray, almost black
    "surface": "#1E1E1E",     # Slightly lighter gray for surfaces like cards/appbar
    "primary": "#BB86FC",     # A vibrant purple that works well on dark backgrounds
    "primary_content": "#000000",
    "text": "#FFFFFF",
    "text_muted": ft.Colors.with_opacity(0.7, "#FFFFFF"),
    "error": "#CF6679",
}

LIGHT_THEME = {
    "background": "#F2F2F2",
    "surface": "#FFFFFF",
    "primary": "#6200EE",
    "primary_content": "#FFFFFF",
    "text": "#000000",
    "text_muted": ft.Colors.with_opacity(0.6, "#000000"),
    "error": "#B00020",
}

# --- Helper Functions ---
def process_text(text):
    raw_paragraphs = re.split(r'\n\s*\n', text.strip())
    paragraphs = []
    for p in raw_paragraphs:
        p = p.strip()
        if not p:
            continue
        if paragraphs and (p.startswith('"') or p.startswith('“') or p.startswith('‘')):
            paragraphs[-1] += "\n\n" + p
        else:
            paragraphs.append(p)
    return paragraphs

def upload_image_to_cloudinary(image_data, public_id):
    try:
        result = uploader.upload(
            image_data,
            folder="visread_images",
            public_id=f"visread_images/{public_id}",
            overwrite=True
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        return None

# --- Main Application Logic ---

def main(page: ft.Page):
    # Set window properties for desktop
    page.title = "VisRead"
    page.window_width = 800
    page.window_height = 720
    page.window_min_width = 600
    page.window_min_height = 600
    
    # Set default theme
    page.theme_mode = ft.ThemeMode.DARK # Default to dark mode now

    def get_theme():
        return DARK_THEME if page.theme_mode == ft.ThemeMode.DARK else LIGHT_THEME

    def update_all_themes():
        theme = get_theme()
        page.bgcolor = theme["background"]
        for view in page.views:
            view.bgcolor = theme["background"]
            if hasattr(view, 'update_theme_colors'):
                view.update_theme_colors()
        page.update()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        update_all_themes()

    def navigate_to(route_path: str, **kwargs):
        if route_path == "login":
            page.views.clear()
            page.views.append(login_view(page, get_theme, navigate_to, toggle_theme))
        elif route_path == "register":
            page.views.append(register_view(page, get_theme, navigate_to, toggle_theme))
        elif route_path == "app":
            page.views.clear()
            page.views.append(app_view(page, get_theme, navigate_to, toggle_theme))
        elif route_path == "reader":
            page.views.append(reader_view(page, get_theme, navigate_to, **kwargs))
        page.update()

    navigate_to("login")

def login_view(page, get_theme, navigate_to, toggle_theme):
    theme = get_theme()
    username_field = ft.TextField(label="Username", border_color=theme["text_muted"], color=theme["text"])
    password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, border_color=theme["text_muted"], color=theme["text"])
    error_msg = ft.Text("", color=theme["error"])

    def do_login(e):
        try:
            response = supabase.table('visread_users').select('*').eq('username', username_field.value).single().execute()
            user_data = response.data
            if user_data and bcrypt.checkpw(password_field.value.encode('utf-8'), user_data["password"].encode("utf-8")):
                global current_user
                current_user = user_data
                navigate_to("app")
            else:
                error_msg.value = "Invalid username or password"
        except Exception as ex:
            error_msg.value = "Invalid username or password"
            print(f"Login error: {ex}")
        page.update()

    view = ft.View(
        "/login",
        [
            ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Image(src="icon.png", width=100, height=100),
                                ft.Text("Welcome Back!", size=32, weight=ft.FontWeight.BOLD, color=theme["text"]),
                                username_field,
                                password_field,
                                ft.ElevatedButton("Login", on_click=do_login, style=ft.ButtonStyle(bgcolor=theme["primary"], color=theme["primary_content"])),
                                ft.TextButton("Don't have an account? Register", on_click=lambda e: navigate_to("register"), style=ft.ButtonStyle(color=theme["primary"])),
                                error_msg,
                            ],
                            spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        width=min(400, page.width - 40 if page.width else 400), padding=20,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True,
            )
        ],
        appbar=ft.AppBar(
            bgcolor=ft.Colors.TRANSPARENT,
            elevation=0,
            actions=[
                ft.Switch(
                    on_change=toggle_theme,
                    value=page.theme_mode == ft.ThemeMode.DARK,
                    active_color=theme["primary"]
                )
            ]
        ),
        scroll=ft.ScrollMode.ADAPTIVE, vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, padding=20, bgcolor=theme["background"]
    )
    def update_theme_colors():
        theme = get_theme()
        view.bgcolor = theme["background"]
        username_field.border_color = theme["text_muted"]
        username_field.color = theme["text"]
        password_field.border_color = theme["text_muted"]
        password_field.color = theme["text"]
        error_msg.color = theme["error"]
        
        # CORRECTED PATH: Access the container's content, then its controls
        container_content = view.controls[0].controls[0].content
        container_content.controls[1].color = theme["text"]
        container_content.controls[4].style.bgcolor = theme["primary"]
        container_content.controls[4].style.color = theme["primary_content"]
        container_content.controls[5].style.color = theme["primary"]
        
        if view.appbar:
            view.appbar.actions[0].value = page.theme_mode == ft.ThemeMode.DARK
            view.appbar.actions[0].active_color = theme["primary"]

    view.update_theme_colors = update_theme_colors
    return view

def register_view(page, get_theme, navigate_to, toggle_theme):
    theme = get_theme()
    username_field = ft.TextField(label="Username", border_color=theme["text_muted"], color=theme["text"])
    password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, border_color=theme["text_muted"], color=theme["text"])
    error_msg = ft.Text("", color=theme["error"])

    def do_register(e):
        try:
            res = supabase.table('visread_users').select('id').eq('username', username_field.value).execute()
            if res.data:
                error_msg.value = "Username already exists!"
            else:
                hashed = bcrypt.hashpw(password_field.value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                supabase.table('visread_users').insert({"username": username_field.value, "password": hashed}).execute()
                page.views.pop()
                page.update()
        except Exception as ex:
            error_msg.value = f"Registration failed: {ex}"
        page.update()

    view = ft.View(
        "/register",
        [
            ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Image(src="icon.png", width=100, height=100),
                                ft.Text("Create Account", size=32, weight=ft.FontWeight.BOLD, color=theme["text"]),
                                username_field,
                                password_field,
                                ft.ElevatedButton("Register", on_click=do_register, style=ft.ButtonStyle(bgcolor=theme["primary"], color=theme["primary_content"])),
                                ft.TextButton("Back to Login", on_click=lambda e: page.views.pop() and page.update(), style=ft.ButtonStyle(color=theme["primary"])),
                                error_msg,
                            ],
                            spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        width=min(400, page.width - 40 if page.width else 400), padding=20,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True,
            )
        ],
        appbar=ft.AppBar(
            bgcolor=ft.Colors.TRANSPARENT,
            elevation=0,
            actions=[
                ft.Switch(
                    on_change=toggle_theme,
                    value=page.theme_mode == ft.ThemeMode.DARK,
                    active_color=theme["primary"]
                )
            ]
        ),
        scroll=ft.ScrollMode.ADAPTIVE, vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, padding=20, bgcolor=theme["background"]
    )
    def update_theme_colors():
        theme = get_theme()
        view.bgcolor = theme["background"]
        username_field.border_color = theme["text_muted"]
        username_field.color = theme["text"]
        password_field.border_color = theme["text_muted"]
        password_field.color = theme["text"]
        error_msg.color = theme["error"]
        
        # CORRECTED PATH: Access the container's content, then its controls
        container_content = view.controls[0].controls[0].content
        container_content.controls[1].color = theme["text"]
        container_content.controls[4].style.bgcolor = theme["primary"]
        container_content.controls[4].style.color = theme["primary_content"]
        container_content.controls[5].style.color = theme["primary"]
        
        if view.appbar:
            view.appbar.actions[0].value = page.theme_mode == ft.ThemeMode.DARK
            view.appbar.actions[0].active_color = theme["primary"]

    view.update_theme_colors = update_theme_colors
    return view

def app_view(page, get_theme, navigate_to, toggle_theme):
    theme = get_theme()
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)

    def show_content(index):
        content_area.controls.clear()
        if index == 0:
            content_view = new_book_view(page, get_theme, navigate_to)
        else:
            content_view = history_view(page, get_theme, navigate_to)
        content_area.controls.append(ft.Row([content_view], alignment=ft.MainAxisAlignment.CENTER, expand=True))
        page.update()

    def nav_changed(e):
        selected_index = e.control.selected_index
        nav_rail.selected_index = selected_index
        nav_bar.selected_index = selected_index
        show_content(selected_index)

    nav_rail = ft.NavigationRail(
        selected_index=0, label_type=ft.NavigationRailLabelType.ALL, min_width=100,
        min_extended_width=400, bgcolor=theme["surface"],
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.CREATE_OUTLINED, selected_icon=ft.Icons.CREATE, label="Create"),
            ft.NavigationRailDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="History"),
        ],
        on_change=nav_changed,
    )
    nav_bar = ft.NavigationBar(
        selected_index=0, bgcolor=ft.Colors.with_opacity(0.95, theme["surface"]),
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.CREATE_OUTLINED, label="Create"),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY, label="History"),
        ],
        on_change=nav_changed,
    )
    main_layout = ft.Row([nav_rail, ft.VerticalDivider(width=1), content_area], expand=True)

    def update_layout_for_resize():
        is_wide = page.width >= 768
        main_layout.controls[0] = nav_rail if is_wide else ft.Container()
        page.navigation_bar = nav_bar if not is_wide else None
        page.update()

    page.on_resize = lambda e: update_layout_for_resize()
    update_layout_for_resize()
    show_content(0)

    view = ft.View(
        "/app",
        [main_layout],
        appbar=ft.AppBar(
            title=ft.Text("VisRead", weight=ft.FontWeight.BOLD, color=theme["text"]),
            bgcolor=theme["surface"],
            actions=[
                ft.Switch(on_change=toggle_theme, value=page.theme_mode == ft.ThemeMode.DARK, active_color=theme["primary"]),
                ft.IconButton(ft.Icons.LOGOUT, on_click=lambda e: navigate_to("login"), icon_color=theme["text_muted"])
            ]
        ),
        padding=0, bgcolor=theme["background"]
    )
    def update_theme_colors():
        theme = get_theme()
        view.bgcolor = theme["background"]
        view.appbar.bgcolor = theme["surface"]
        view.appbar.title.color = theme["text"]
        view.appbar.actions[0].value = page.theme_mode == ft.ThemeMode.DARK
        view.appbar.actions[1].icon_color = theme["text_muted"]
        nav_rail.bgcolor = theme["surface"]
        nav_bar.bgcolor = ft.Colors.with_opacity(0.95, theme["surface"])
        show_content(nav_rail.selected_index)
    view.update_theme_colors = update_theme_colors
    return view

def new_book_view(page, get_theme, navigate_to):
    theme = get_theme()
    title_field = ft.TextField(label="Book Title", border_color=theme["text_muted"], color=theme["text"])
    author_field = ft.TextField(label="Author", border_color=theme["text_muted"], color=theme["text"])
    content_field = ft.TextField(label="Paste your story here...", multiline=True, min_lines=8, border_color=theme["text_muted"], color=theme["text"])
    error_msg = ft.Text("", color=theme["error"])

    def on_submit(e):
        if not title_field.value or not content_field.value:
            error_msg.value = "Title and content are required."
            page.update()
            return
        chapters = process_text(content_field.value)
        book_doc = {
            "title": title_field.value, "author": author_field.value, "chapters": chapters,
            "user_id": current_user["id"], "images": {},
        }
        try:
            response = supabase.table('visread_books').insert(book_doc).execute()
            new_book_id = response.data[0]['id']
            navigate_to("reader", book_id=new_book_id, page_index=0)
        except Exception as ex:
            error_msg.value = f"Failed to create book: {ex}"
            page.update()

    return ft.Container(
        ft.Column([
            ft.Text("Create a New Story", size=24, weight=ft.FontWeight.BOLD, color=theme["text"]),
            title_field, author_field, content_field,
            ft.ElevatedButton("Generate Book", on_click=on_submit, style=ft.ButtonStyle(bgcolor=theme["primary"], color=theme["primary_content"])),
            error_msg
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, scroll=ft.ScrollMode.ADAPTIVE),
        padding=20, alignment=ft.alignment.top_center, expand=True
    )

def history_view(page, get_theme, navigate_to):
    theme = get_theme()
    try:
        response = supabase.table('visread_books').select('*').eq('user_id', current_user['id']).order('created_at', desc=True).execute()
        book_list = response.data
    except Exception as ex:
        book_list = []
        print(f"Error fetching history: {ex}")

    def create_book_card(book):
        return ft.Card(
            ft.Container(
                ft.ListTile(
                    title=ft.Text(book.get('title', 'No Title'), color=theme["text"]),
                    subtitle=ft.Text(f"by {book.get('author', 'Unknown Author')}", color=theme["text_muted"]),
                    on_click=lambda e, bid=book["id"]: navigate_to("reader", book_id=bid, page_index=0),
                    trailing=ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color=theme["text_muted"]),
                ),
                padding=ft.padding.symmetric(vertical=5)
            ),
            color=theme["surface"], elevation=2
        )

    controls = [create_book_card(book) for book in book_list] if book_list else [ft.Text("No books found.", color=theme["text"])]
    return ft.Container(
        ft.Column([
            ft.Text("Reading History", size=24, weight=ft.FontWeight.BOLD, color=theme["text"]),
            *controls
        ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE),
        padding=20, expand=True, alignment=ft.alignment.top_center
    )

def reader_view(page, get_theme, navigate_to, book_id: int, page_index: int = 0):
    theme = get_theme()
    try:
        response = supabase.table('visread_books').select('*').eq('id', book_id).single().execute()
        book = response.data
    except Exception as ex:
        return ft.View(appbar=ft.AppBar(title=ft.Text("Error"), bgcolor=theme["surface"]), controls=[ft.Text("Book not found", color=theme["error"])])

    chapters = book.get("chapters", [])
    images = book.get("images", {})
    image_url = images.get(str(page_index))
    image_display = ft.Container(
        ft.ProgressRing(color=theme["primary"]),
        width=MAX_CONTENT_WIDTH, height=300, bgcolor=ft.Colors.with_opacity(0.1, theme["text"]),
        border_radius=12, alignment=ft.alignment.center
    )

    def update_image(url):
        image_display.content = ft.Image(src=url, border_radius=12, fit=ft.ImageFit.COVER)
        image_display.height = None
        page.update()

    def handle_image_generation():
        if image_url:
            update_image(image_url)
            return
        if page_index < len(chapters):
            prompt = chapters[page_index]
            image_data = generate_image(prompt)
            if image_data:
                public_id = f"{book_id}_{page_index}"
                new_url = upload_image_to_cloudinary(image_data, public_id)
                if new_url:
                    images[str(page_index)] = new_url
                    supabase.table('visread_books').update({'images': images}).eq('id', book_id).execute()
                    update_image(new_url)
            else:
                image_display.content = ft.Text("Image generation failed.", color=theme["error"])
            page.update()
    
    page.run_thread(handle_image_generation)

    def go_back(e):
        page.views.pop()
        page.update()

    def go_prev(e):
        if page_index > 0:
            page.views[-1] = reader_view(page, get_theme, navigate_to, book_id=book_id, page_index=page_index - 1)
            page.update()
    
    def go_next(e):
        if page_index + 1 < len(chapters):
            page.views[-1] = reader_view(page, get_theme, navigate_to, book_id=book_id, page_index=page_index + 1)
            page.update()

    view = ft.View(
        f"/reader/{book_id}/{page_index}",
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            image_display,
                            ft.Text(f"Chapter {page_index + 1}", size=24, weight=ft.FontWeight.BOLD, color=theme["text"]),
                            ft.Text(
                                chapters[page_index] if page_index < len(chapters) else "End of Book",
                                color=theme["text_muted"], text_align=ft.TextAlign.JUSTIFY
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(ft.Icons.ARROW_BACK_IOS, on_click=go_prev, disabled=page_index == 0),
                                    ft.IconButton(ft.Icons.ARROW_FORWARD_IOS, on_click=go_next, disabled=page_index + 1 >= len(chapters)),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        ],
                        spacing=20, scroll=ft.ScrollMode.ADAPTIVE, expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER, expand=True
            )
        ],
        appbar=ft.AppBar(
            title=ft.Text(book["title"]),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS, on_click=go_back),
            bgcolor=theme["surface"], color=theme["text"]
        ),
        padding=20, scroll=ft.ScrollMode.ADAPTIVE, bgcolor=theme["background"]
    )
    def update_theme_colors():
        theme = get_theme()
        view.bgcolor = theme["background"]
        view.appbar.bgcolor = theme["surface"]
        view.appbar.title.color = theme["text"]
        view.appbar.leading.icon_color = theme["text"]
    view.update_theme_colors = update_theme_colors
    return view

# --- Application Entry Point for Desktop ---
if __name__ == "__main__":
    ft.app(
        target=main,
        assets_dir="src/assets"
    )
