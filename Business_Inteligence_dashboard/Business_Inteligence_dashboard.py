import reflex as rx
import pandas as pd
from io import StringIO
import datetime

# --- CONFIG & STYLE ---
# Palet Warna Elegan (Ungu & Putih)
COLORS = {
    "primary": "#6200EA",      # Ungu Utama (Deep Purple)
    "secondary": "#B388FF",    # Ungu Muda
    "bg_main": "#F3F4F6",      # Abu-abu sangat muda (Background)
    "bg_card": "#FFFFFF",      # Putih (Kartu)
    "text_dark": "#1F2937",    # Hitam/Abu tua
    "text_light": "#6B7280",   # Abu-abu text
    "border": "#E5E7EB",       # Border halus
}

# --- STATE (BACKEND LOGIC) ---
class DashboardState(rx.State):
    # Data Mentah
    raw_data: list[dict] = []
    
    # KPI Metrics
    total_revenue: float = 0
    total_orders: int = 0
    aov: float = 0
    active_customers: int = 0
    
    # Data Khusus Grafik (Aggregated Data)
    trend_data: list[dict] = []
    category_data: list[dict] = []
    city_data: list[dict] = []
    payment_data: list[dict] = []

    # Chatbot State
    chat_history: list[list[str]] = [
        ["AI", "Halo. Selamat datang di Dibimbing Dashboard. Ada yang bisa saya bantu analisis?"]
    ]
    chat_input: str = ""

    # --- COMPUTED VARS (FORMATTER) ---
    @rx.var
    def revenue_fmt(self) -> str:
        return f"Rp {self.total_revenue:,.0f}"

    @rx.var
    def orders_fmt(self) -> str:
        return f"{self.total_orders:,}"

    @rx.var
    def aov_fmt(self) -> str:
        return f"Rp {self.aov:,.0f}"

    # --- ETL PROCESS ---
    def load_data(self):
        # URL Sheet yang sudah dikonversi ke format Export CSV
        # GID 678977029 adalah sheet 'Dataset Dummy' dari link Anda
        sheet_url = "https://docs.google.com/spreadsheets/d/1M4ZG7-CsPGvhyU7_YHOSUo-dssu-jSs0E4ralASFg60/export?format=csv&gid=678977029"
        
        try:
            df = pd.read_csv(sheet_url)

            # 1. Data Cleaning
            # Hapus % dan convert ke float
            df['discount_applied'] = df['discount_applied'].astype(str)
            df['discount_float'] = df['discount_applied'].str.rstrip('%').replace('nan', '0').replace('', '0').astype('float') / 100
            
            # Hitung Net Revenue
            df['gross_amount'] = df['price'] * df['quantity']
            df['net_revenue'] = df['gross_amount'] * (1 - df['discount_float'])
            
            # Format Tanggal
            df['order_date'] = pd.to_datetime(df['order_date'])
            df['date_str'] = df['order_date'].dt.strftime('%Y-%m-%d')

            # 2. Hitung KPI Utama
            self.total_revenue = df['net_revenue'].sum()
            self.total_orders = int(df['order_id'].nunique())
            self.active_customers = int(df['order_id'].count()) # Atau unique customer_id jika ada
            
            if self.total_orders > 0:
                self.aov = self.total_revenue / self.total_orders
            else:
                self.aov = 0

            # 3. Siapkan Data untuk Grafik (Aggregation)
            
            # Grafik 1: Revenue per Category
            cat_grp = df.groupby('product_category')['net_revenue'].sum().reset_index()
            self.category_data = cat_grp.to_dict('records')

            # Grafik 2: Daily Trend
            trend_grp = df.groupby('date_str')['net_revenue'].sum().reset_index()
            self.trend_data = trend_grp.to_dict('records')

            # Grafik 3: Revenue per City
            city_grp = df.groupby('customer_city')['net_revenue'].sum().reset_index().sort_values('net_revenue', ascending=False)
            self.city_data = city_grp.to_dict('records')

            # Grafik 4: Payment Method
            pay_grp = df.groupby('payment_method')['order_id'].count().reset_index()
            pay_grp.columns = ['name', 'value'] # Rename untuk Pie Chart
            self.payment_data = pay_grp.to_dict('records')

        except Exception as e:
            print(f"Error loading data: {e}")
            # Fallback jika error (biar UI tidak crash)
            self.chat_history.append(["AI", "Gagal memuat data dari Google Sheets. Cek koneksi internet atau format data."])

    def handle_chat(self):
        if not self.chat_input:
            return
            
        user_msg = self.chat_input.lower()
        response = ""
        
        # Logika Chatbot Simple
        if "prediksi" in user_msg:
            pred = self.total_revenue * 1.2
            response = f"Analisis Prediktif: Berdasarkan tren saat ini, diproyeksikan pendapatan bulan depan mencapai Rp {pred:,.0f} (Growth +20%)."
        elif "kota" in user_msg or "terlaris" in user_msg:
            # Cari kota top 1
            if self.city_data:
                top_city = self.city_data[0]['customer_city']
                response = f"Insight Wilayah: Kota dengan kontribusi pendapatan terbesar adalah {top_city}."
            else:
                response = "Data wilayah belum tersedia."
        elif "kategori" in user_msg:
             response = "Saran Stok: Pertahankan stok untuk kategori Home Living dan Fashion karena memiliki margin tinggi."
        else:
            response = "Saya dapat membantu menghitung prediksi revenue, analisis kota terlaris, atau performa kategori."

        self.chat_history.append(["User", self.chat_input])
        self.chat_history.append(["AI", response])
        self.chat_input = ""

    def set_chat_input(self, val):
        self.chat_input = val

# --- UI COMPONENTS ---

def card_kpi(title: str, value: str, icon_tag: str):
    return rx.vstack(
        rx.hstack(
            rx.icon(tag=icon_tag, size=20, color=COLORS["primary"]),
            rx.text(title, font_size="0.85em", font_weight="500", color=COLORS["text_light"]),
            spacing="2",
            align_items="center"
        ),
        rx.text(value, font_size="1.8em", font_weight="700", color=COLORS["text_dark"]),
        padding="20px",
        bg=COLORS["bg_card"],
        border_radius="12px",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)",
        border=f"1px solid {COLORS['border']}",
        width="100%",
        align_items="flex-start",
    )

def chart_container(title: str, component):
    return rx.vstack(
        rx.text(title, font_size="1em", font_weight="600", color=COLORS["text_dark"], margin_bottom="15px"),
        component,
        padding="24px",
        bg=COLORS["bg_card"],
        border_radius="12px",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)",
        border=f"1px solid {COLORS['border']}",
        width="100%",
        height="100%",
    )

def chat_bubble(sender: str, text: str):
    is_ai = sender == "AI"
    return rx.hstack(
        rx.cond(
            is_ai,
            rx.icon(tag="bot", size=24, color=COLORS["primary"]),
            rx.spacer()
        ),
        rx.box(
            rx.text(text, font_size="0.9em"),
            bg=rx.cond(is_ai, COLORS["primary"], "#E5E7EB"),
            color=rx.cond(is_ai, "white", COLORS["text_dark"]),
            padding="12px 16px",
            border_radius="12px",
            border_top_left_radius=rx.cond(is_ai, "12px", "2px"),
            border_top_right_radius=rx.cond(is_ai, "2px", "12px"),
            max_width="80%",
        ),
        rx.cond(
            is_ai,
            rx.spacer(),
            rx.icon(tag="user", size=24, color=COLORS["text_light"])
        ),
        align_items="flex-start",
        width="100%",
        justify_content=rx.cond(is_ai, "flex-start", "flex-end"),
        margin_bottom="10px",
    )

# --- MAIN PAGE ---
def index():
    return rx.box(
        rx.vstack(
            # HEADER
            rx.hstack(
                rx.vstack(
                    rx.heading("Dibimbing Dashboard", size="6", color=COLORS["primary"], letter_spacing="-0.02em"),
                    rx.text("Real-time Sales Monitoring System", font_size="0.9em", color=COLORS["text_light"]),
                    spacing="1"
                ),
                rx.spacer(),
                rx.button(
                    rx.icon(tag="refresh-cw", size=16),
                    "Refresh Data",
                    on_click=DashboardState.load_data,
                    variant="soft",
                    color_scheme="violet",
                    size="2",
                ),
                width="100%",
                padding_y="20px",
                border_bottom=f"1px solid {COLORS['border']}",
                margin_bottom="20px",
            ),

            # KPI GRID
            rx.grid(
                card_kpi("Total Net Revenue", DashboardState.revenue_fmt, "dollar-sign"),
                card_kpi("Total Orders", DashboardState.orders_fmt, "shopping-bag"),
                card_kpi("Avg. Order Value", DashboardState.aov_fmt, "trending-up"),
                card_kpi("Customers", "Active", "users"),
                columns="4",
                spacing="4",
                width="100%",
                margin_bottom="24px",
            ),

            # CHARTS SECTION 1
            rx.grid(
                # Chart 1: Tren Revenue (Area Chart)
                chart_container(
                    "Revenue Trend (Daily)",
                    rx.recharts.area_chart(
                        rx.recharts.area(
                            data_key="net_revenue", 
                            stroke=COLORS["primary"], 
                            fill=COLORS["secondary"],
                            fill_opacity=0.3
                        ),
                        rx.recharts.x_axis(data_key="date_str", font_size=12),
                        rx.recharts.y_axis(font_size=12),
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                        rx.recharts.tooltip(),
                        data=DashboardState.trend_data,
                        height=250,
                        width="100%",
                    )
                ),
                # Chart 2: Revenue by Category (Bar Chart)
                chart_container(
                    "Revenue by Category",
                    rx.recharts.bar_chart(
                        rx.recharts.bar(
                            data_key="net_revenue", 
                            fill=COLORS["primary"], 
                            radius=[4, 4, 0, 0]
                        ),
                        rx.recharts.x_axis(data_key="product_category", font_size=12),
                        rx.recharts.y_axis(font_size=12),
                        rx.recharts.tooltip(),
                        data=DashboardState.category_data,
                        height=250,
                        width="100%",
                    )
                ),
                columns="2",
                spacing="4",
                width="100%",
                margin_bottom="24px",
            ),

            # CHARTS SECTION 2 & CHATBOT
            rx.grid(
                # Kiri: Chart 3 & 4
                rx.vstack(
                    # Chart 3: Top Cities (Bar Horizontal)
                    chart_container(
                        "Top Cities by Revenue",
                        rx.recharts.bar_chart(
                            rx.recharts.bar(
                                data_key="net_revenue", 
                                fill=COLORS["primary"],
                                bar_size=20
                            ),
                            rx.recharts.x_axis(type_="number", hide=True),
                            rx.recharts.y_axis(data_key="customer_city", type_="category", width=80, font_size=12),
                            rx.recharts.tooltip(),
                            layout="vertical",
                            data=DashboardState.city_data,
                            height=200,
                            width="100%",
                        )
                    ),
                    # Chart 4: Payment Method (Pie Chart)
                    chart_container(
                        "Payment Method Distribution",
                        rx.recharts.pie_chart(
                            rx.recharts.pie(
                                data=DashboardState.payment_data,
                                data_key="value",
                                name_key="name",
                                cx="50%",
                                cy="50%",
                                outer_radius=60,
                                fill=COLORS["primary"],
                                label=True,
                            ),
                            rx.recharts.tooltip(),
                            height=200,
                            width="100%",
                        )
                    ),
                    width="100%",
                    spacing="4",
                ),
                
                # Kanan: Chatbot Assistant
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="sparkles", color=COLORS["primary"]),
                        rx.text("AI Business Assistant", font_weight="600"),
                        border_bottom=f"1px solid {COLORS['border']}",
                        padding_bottom="15px",
                        width="100%",
                        margin_bottom="10px"
                    ),
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                DashboardState.chat_history,
                                lambda msg: chat_bubble(msg[0], msg[1])
                            ),
                            width="100%",
                            gap="2"
                        ),
                        height="350px",
                        type="hover",
                        scrollbars="vertical",
                    ),
                    rx.hstack(
                        rx.input(
                            placeholder="Ketik 'prediksi' atau 'kota'...",
                            value=DashboardState.chat_input,
                            on_change=DashboardState.set_chat_input,
                            variant="soft",
                            radius="full",
                            width="100%",
                        ),
                        rx.button(
                            rx.icon(tag="send", size=18),
                            on_click=DashboardState.handle_chat,
                            radius="full",
                            color_scheme="violet",
                        ),
                        width="100%",
                        padding_top="10px"
                    ),
                    bg=COLORS["bg_card"],
                    border=f"1px solid {COLORS['border']}",
                    border_radius="12px",
                    padding="20px",
                    box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)",
                    height="100%",
                    width="100%",
                ),
                columns="2",
                spacing="4",
                width="100%",
            ),

            max_width="1280px",
            padding="30px",
            margin="0 auto",
        ),
        bg=COLORS["bg_main"],
        min_height="100vh",
        font_family="Inter, sans-serif",
        on_mount=DashboardState.load_data,
    )

app = rx.App()
app.add_page(index)