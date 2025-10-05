--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.8 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: places; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.places (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    url text NOT NULL,
    photo text,
    description text,
    entity_types character varying[] NOT NULL,
    atmosphere_tags character varying[] NOT NULL,
    purpose_tags character varying[] NOT NULL,
    features character varying[] NOT NULL,
    best_time character varying(20),
    working_days character varying[] NOT NULL,
    budget_level character varying(20),
    opening_hours character varying(100),
    is_24_7 boolean,
    overall_rating double precision,
    review_count integer
);


ALTER TABLE public.places OWNER TO postgres;

--
-- Name: places_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.places_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.places_id_seq OWNER TO postgres;

--
-- Name: places_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.places_id_seq OWNED BY public.places.id;


--
-- Name: places id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.places ALTER COLUMN id SET DEFAULT nextval('public.places_id_seq'::regclass);


--
-- Data for Name: places; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.places (id, title, url, photo, description, entity_types, atmosphere_tags, purpose_tags, features, best_time, working_days, budget_level, opening_hours, is_24_7, overall_rating, review_count) FROM stdin;
13	Латук	https://go.2gis.com/VCWdL	static/photos/20251004193052_207628__2025-10-04_19.28.43.png		{ресторан,кафе}	{уютный,спокойный,семейный,туристический,популярный}	{свидание,друзья,наедине,празднование,обед,ужин}	{танцы,Wi-Fi,мероприятия,"бесплатный вход",бронирование,доставка,"еда на вынос"}	день	{}	средний	12:00-22:00	f	4.8	30
14	Blanc	https://go.2gis.com/d3Okl	static/photos/20251004193305_037119__2025-10-04_19.33.01.png		{ресторан}	{романтичный,спокойный,элегантный,премиум,богемный,вечерний}	{свидание,друзья,работа,учеба,наедине,бизнес,ужин}	{"живая музыка",Wi-Fi,парковка,"бесплатный вход",бронирование,доставка,"еда на вынос"}	вечер	{}	дорогой	9:00-24:00	f	4.2	150
15	Pasta на Солянке	https://go.2gis.com/x2DP4	static/photos/20251004202318_970778__2025-10-04_20.23.13.png		{ресторан}	{уютный,романтичный,спокойный,элегантный,премиум,семейный,дневной,вечерний}	{свидание,работа,наедине,бизнес,"быстрый визит",обед,ужин}	{Wi-Fi,"место для курения",алкоголь,"бесплатный вход",бронирование,доставка,"еда на вынос"}	день	{}	дорогой	12:00 - 24:00	f	4.8	1076
9	Megobari	https://go.2gis.com/6qVtX	static/photos/20251004192501_879771__2025-10-04_19.24.47.png		{ресторан,бар}	{}	{свидание,друзья,празднование,ужин}	{Wi-Fi,"место для курения",алкоголь,"бесплатный вход",бронирование,"еда на вынос"}	вечер	{пн,вт,ср,чт,пт,сб,вс}	средний	12:00-24:00	f	4.6	102
10	Ткемали	https://go.2gis.com/qHqjC	static/photos/20251004192818_599701__2025-10-04_19.28.08.png		{ресторан}	{уютный,шумный,энергичный,элегантный,семейный,туристический,популярный,вечерний}	{свидание,празднование,"быстрый визит",ужин}	{Wi-Fi,"место для курения",алкоголь,мероприятия}	вечер	{}	средний	12:00-24:00	f	5	221
16	Bla bla bar	https://go.2gis.com/DbKU5	static/photos/20251004202835_135252__2025-10-04_20.28.29.png		{ресторан,клуб}	{шумный,энергичный,ночной}	{друзья}	{танцы,"место для курения",алкоголь}	ночь	{}	средний	12:00-06:00	f	4.7	406
17	Everest Siberia	https://go.2gis.com/GXW7m	static/photos/20251004203226_446934__2025-10-04_20.29.04.png		{бар,клуб}	{шумный,энергичный,артхаусный}	{друзья,празднование}	{"живая музыка"}	ночь	{}	средний	10:00-05:00	f	5	274
18	Сквер у памятника Карлу Марксу	https://go.2gis.com/Sz9wn	static/photos/20251004224040_955892__2025-10-04_22.40.00.png		{парк}	{уютный,романтичный,спокойный,семейный,туристический,популярный}	{свидание,друзья,наедине,"быстрый визит",фотосъемка,прогулки,"осмотр достопримечательностей"}	{"для отдыха на природе"}	день	{}	бюджетный	00:00-24:00	f	5	10
19	Dr.Живаго	https://go.2gis.com/0wU6R	static/photos/Снимок экрана 2025-10-04 в 21.45.34.png	Dr.Живаго, ресторан - ресторан с премиум, романтичный атмосферой в самом сердце Москвы	{ресторан}	{премиум,романтичный,элегантный}	{ужин,празднование,свидание,бизнес,"деловой обед"}	{"живая музыка",вегетарианец,алкоголь,бронирование}	ночь	{}	средний	00:00-24:00	f	4.7	0
20	Рыба моя	https://go.2gis.com/e5HRl	static/photos/Снимок экрана 2025-10-04 в 21.47.13.png	Рыба моя, рыбный ресторан - ресторан с премиум, романтичный атмосферой в самом сердце Москвы	{ресторан}	{премиум,романтичный,элегантный}	{ужин,празднование,свидание,бизнес,"деловой обед"}	{"живая музыка",вегетарианец,алкоголь,бронирование}	день	{}	средний	12:00-24:00	f	4.5	0
21	Белуга	https://go.2gis.com/d84O3	static/photos/Снимок экрана 2025-10-04 в 21.48.09.png	Белуга, ресторан современной российской кухни - ресторан с премиум, романтичный атмосферой в самом сердце Москвы	{ресторан}	{премиум,романтичный,элегантный}	{ужин,празднование,свидание,бизнес,"деловой обед"}	{"живая музыка",вегетарианец,алкоголь,бронирование}	день	{}	средний	12:00-24:00	f	5	0
22	Корчма	https://go.2gis.com/81YJh	static/photos/Снимок экрана 2025-10-04 в 21.52.03.png	Корчма - кафе с уютный, домашний атмосферой в самом сердце Москвы	{кафе}	{уютный,домашний,непринужденный}	{друзья,работа,"быстрый визит",обед,перекус}	{"еда на вынос",Wi-Fi,вегетарианец,"доступная среда"}	день	{}	бюджетный	09:00-02:00	f	4.4	0
23	КонтрРазведка	https://go.2gis.com/y3C8E	static/photos/Снимок экрана 2025-10-04 в 22.10.24.png	КонтрРазведка, бар - бар с энергичный, вечерний атмосферой в самом сердце Москвы	{бар}	{энергичный,вечерний,шумный,дружеский}	{друзья,вечеринка,релакс,алкоголь,знакомства}	{караоке,"живая музыка",алкоголь,танцы}	ночь	{}	средний	12:00-05:00	f	4.2	0
24	Savva	https://go.2gis.com/sIG2A	static/photos/Снимок экрана 2025-10-04 в 22.11.11.png	Savva, ресторан - ресторан с премиум, романтичный атмосферой в самом сердце Москвы	{ресторан}	{премиум,романтичный,элегантный}	{ужин,празднование,свидание,бизнес,"деловой обед"}	{"живая музыка",вегетарианец,алкоголь,бронирование}	вечер	{}	средний	12:00 до 24:00	f	5	0
31	Manul	https://go.2gis.com/VUP1e	static/photos/Снимок экрана 2025-10-04 в 22.11.11.png	Manul, ресторан - ресторан с премиум, романтичный атмосферой в самом сердце Москвы	{ресторан}	{премиум,романтичный,элегантный}	{ужин,празднование,свидание,бизнес,"деловой обед"}	{"живая музыка",вегетарианец,алкоголь,бронирование}	вечер	{}	средний	12:00-24:00	f	4.5	0
46	Бюст кардиолога А.Л.Мясникова	https://go.2gis.com/6DUYt	static/photos\\20251004214220_209861_image.png		{памятник}	{туристический,популярный}	{прогулки,"осмотр достопримечательностей"}	{"бесплатный вход"}	день	{}	бюджетный		t	5	10
47	Бюст Петра I	https://go.2gis.com/NJ8QJ	static/photos\\20251004220507_513231_image.png		{памятник}	{туристический}	{прогулки,"осмотр достопримечательностей"}	{"бесплатный вход"}	день	{}	бюджетный		t	5	7
48	Колокольня Знаменского Монастыря	https://go.2gis.com/DZ2FZ	static/photos\\20251004221033_915708_image.png		{церковь,храм}	{туристический,популярный}	{прогулки,"осмотр достопримечательностей"}	{"бесплатный вход"}	день	{}	бюджетный	10:00-19:00	f	5	2
49	Храм Богоявления Господня бывшего Богоявленского монастыря	https://go.2gis.com/p6uRw	static/photos\\20251004221228_525934_image.png		{храм}	{туристический}	{наедине,"осмотр достопримечательностей"}	{"бесплатный вход"}	утро	{}	бюджетный	8:00-21:00	f	4.9	8
50	Храм Рождества Пресвятой Богородицы на Кулишках	https://go.2gis.com/WrScv	static/photos\\20251004221414_550830_image.png		{храм}	{туристический}	{"осмотр достопримечательностей"}	{"бесплатный вход"}	день	{}	бюджетный	8:00-20:00	f	5	6
51	Храм святых Бессребренников Космы и Дамиана на Маросейке	https://go.2gis.com/VdE8W	static/photos\\20251004221620_538517_image.png		{храм}	{туристический}	{"осмотр достопримечательностей"}	{"бесплатный вход"}	день	{}	бюджетный	8:00-19:00	f	4.4	8
52	Евангелическо-лютеранский кафедральный собор святых Петра и Павла	https://go.2gis.com/C7g36	static/photos\\20251004223818_783780_image.png		{"кафедральный собор"}	{туристический,популярный}	{"осмотр достопримечательностей"}	{"платный вход"}	день	{}	бюджетный	10:00-19:00	f	4.8	105
53	Храм Святителя Николая в Кленниках	https://go.2gis.com/J69MK	static/photos\\20251004224114_906842_image.png		{храм}	{туристический,популярный}	{"осмотр достопримечательностей"}	{"платный вход"}	день	{}	бюджетный	8:00-19:00	f	4.9	14
32	La Bottega Siciliana	https://go.2gis.com/7hvOc	static/photos/Снимок экрана 2025-10-04 в 22.14.32.png	La Bottega Siciliana, ресторан сицилийской кухни - ресторан с премиум, романтичный атмосферой в самом сердце Москвы	{ресторан}	{премиум,романтичный,элегантный}	{ужин,празднование,свидание,бизнес,"деловой обед"}	{"живая музыка",вегетарианец,алкоголь,бронирование}	вечер	{}	средний	10:00 до 24:00	f	5	0
33	Страна которой нет	https://go.2gis.com/vzfbD	static/photos/Снимок экрана 2025-10-04 в 22.29.15.png	Страна которой нет, ресторан - ресторан с премиум, романтичный атмосферой в самом сердце Москвы	{ресторан}	{премиум,романтичный,элегантный}	{ужин,празднование,свидание,бизнес,"деловой обед"}	{"живая музыка",вегетарианец,алкоголь,бронирование}	вечер	{}	средний	12:00-01:00	f	4.6	0
34	Страна которой нет	https://go.2gis.com/vzfbD	static/photos/Снимок экрана 2025-10-04 в 22.29.15.png	Страна которой нет, ресторан - ресторан с премиум, романтичный атмосферой в самом сердце Москвы	{ресторан}	{премиум,романтичный,элегантный}	{ужин,празднование,свидание,бизнес,"деловой обед"}	{"живая музыка",вегетарианец,алкоголь,бронирование}	вечер	{}	средний	12:00-01:00	f	4.6	0
35	Палаты Бояр Романовых	https://go.2gis.com/fy2et	static/photos\\20251004203126_715502_image.png		{музей}	{туристический,популярный}	{прогулки,"осмотр достопримечательностей"}	{мероприятия,"платный вход"}		{}	бюджетный	10:00-18:00	f	4.4	52
36	Старый Английский Двор	https://go.2gis.com/WValG	static/photos\\20251004203515_787364_image.png		{музей,"историческое здание","внутренний двор"}	{тихий,спокойный,семейный,туристический}	{прогулки,"осмотр достопримечательностей"}	{мероприятия,"платный вход"}	день	{}	бюджетный	10:00-18:45	f	4.5	88
37	Музей Отечественной войны 1812 года	https://go.2gis.com/exZEF	static/photos\\20251004204021_316779_image.png		{музей}	{туристический,популярный}	{прогулки}	{"платный вход"}	день	{}	средний	10:00-21:00	f	4.9	93
38	Подземный музей	https://go.2gis.com/Awpk4	static/photos\\20251004204249_826916_image.png		{музей}	{семейный,туристический,популярный}	{прогулки,"осмотр достопримечательностей"}	{доступно,"платный вход"}	день	{}	бюджетный	10:00-21:00	f	4	20
39	Смотровая площадка	https://go.2gis.com/TtbYB	static/photos\\20251004212620_648214_image.png		{"смотровая площадка"}	{туристический,популярный}	{прогулки,"осмотр достопримечательностей"}	{"бесплатный вход"}	вечер	{}	бюджетный		t	5	1
40	ЦДМ	https://go.2gis.com/peGkW	static/photos\\20251004212759_689420_image.png		{"смотровая площадка"}	{семейный,туристический,популярный}	{фотосъемка,"осмотр достопримечательностей"}	{"платный вход"}	вечер	{}	бюджетный	10:00-22:30	f	4.3	24
41	Видовой Холм, парк Зарядье	https://go.2gis.com/z1iK7	static/photos\\20251004212956_304485_image.png		{"смотровая площадка"}	{семейный,туристический,популярный,местный}	{фотосъемка,прогулки,"осмотр достопримечательностей"}	{"бесплатный вход"}	день	{}	бюджетный		t	4.8	20
42	Москворецкая набережная	https://go.2gis.com/SXomv	static/photos\\20251004213244_782337_image.png		{набережная}	{семейный,туристический,местный}	{фотосъемка,прогулки,"осмотр достопримечательностей"}	{"бесплатный вход"}	вечер	{}	бюджетный		t	4.5	2
43	Кремлёвская набережная	https://go.2gis.com/vO8jL	static/photos\\20251004213425_435259_image.png		{набережная}	{семейный,туристический,популярный,вечерний,ночной}	{фотосъемка,прогулки}	{"бесплатный вход"}	вечер	{}	бюджетный		t	4.6	6
44	Памятник Кириллу и Мефодию	https://go.2gis.com/nZujh	static/photos\\20251004213842_690060_image.png		{памятник}	{туристический,популярный}	{прогулки,"осмотр достопримечательностей"}	{"бесплатный вход"}	день	{}	бюджетный		t	5	9
45	Памятник О.Э.Мандельштаму	https://go.2gis.com/CWgIH	static/photos\\20251004214027_850517_image.png		{памятник}	{туристический,популярный}	{прогулки,"осмотр достопримечательностей"}	{"бесплатный вход"}	день	{}	бюджетный		t	5	4
54	Монумент в память о жертвах трагедии в Беслане	https://go.2gis.com/332pi	static/photos\\20251004230331_315536_image.png		{скульптура}	{туристический,популярный}	{"осмотр достопримечательностей"}	{"бесплатный вход"}	день	{}	бюджетный		t	5	3
55	Новый Манеж 	https://go.2gis.com/HqYTI	\N	это очень красивое место. здесь нельзя покушать, покурить, но можно просто им полюбоваться	{}	{романтичный}	{свидание}	{}	вечер	{}	\N	\N	f	0	0
56	Ego Music	https://go.2gis.com/yCk4o	static/photos/a571fdfc-d45b-4063-826e-367a5a181c51.png	очень классное место, чтобы порепетировать музыку, мы там часто репетируем с друзьями	{студия}	{}	{друзья}	{"место для курения"}	день	{}	\N	\N	f	0	0
\.


--
-- Name: places_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.places_id_seq', 56, true);


--
-- Name: places places_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.places
    ADD CONSTRAINT places_pkey PRIMARY KEY (id);


--
-- Name: ix_places_atmosphere_tags; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_places_atmosphere_tags ON public.places USING gin (atmosphere_tags);


--
-- Name: ix_places_budget_level; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_places_budget_level ON public.places USING btree (budget_level);


--
-- Name: ix_places_entity_types; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_places_entity_types ON public.places USING gin (entity_types);


--
-- Name: ix_places_features; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_places_features ON public.places USING gin (features);


--
-- Name: ix_places_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_places_id ON public.places USING btree (id);


--
-- Name: ix_places_purpose_tags; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_places_purpose_tags ON public.places USING gin (purpose_tags);


--
-- Name: ix_places_rating; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_places_rating ON public.places USING btree (overall_rating DESC);


--
-- Name: ix_places_rating_reviews; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_places_rating_reviews ON public.places USING btree (overall_rating DESC, review_count DESC);


--
-- Name: ix_places_review_count; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_places_review_count ON public.places USING btree (review_count DESC);


--
-- Name: ix_places_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_places_title ON public.places USING btree (title);


--
-- PostgreSQL database dump complete
--

