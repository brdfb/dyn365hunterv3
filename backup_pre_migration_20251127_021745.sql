--
-- PostgreSQL database dump
--

\restrict VARZgznU9LU69WWxQSQ7qhOvWVdULvhVyp1LmbkLcI4pA3l4edhswBQOnQ1ptVa

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: dyn365hunter
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO dyn365hunter;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: dyn365hunter
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO dyn365hunter;

--
-- Name: alert_config; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.alert_config (
    id integer NOT NULL,
    user_id character varying(255) NOT NULL,
    alert_type character varying(50) NOT NULL,
    notification_method character varying(50) NOT NULL,
    enabled boolean NOT NULL,
    frequency character varying(50) NOT NULL,
    webhook_url text,
    email_address character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.alert_config OWNER TO dyn365hunter;

--
-- Name: alert_config_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.alert_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.alert_config_id_seq OWNER TO dyn365hunter;

--
-- Name: alert_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.alert_config_id_seq OWNED BY public.alert_config.id;


--
-- Name: alerts; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.alerts (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    alert_type character varying(50) NOT NULL,
    alert_message text NOT NULL,
    status character varying(50) NOT NULL,
    notification_method character varying(50),
    sent_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.alerts OWNER TO dyn365hunter;

--
-- Name: alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.alerts_id_seq OWNER TO dyn365hunter;

--
-- Name: alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.alerts_id_seq OWNED BY public.alerts.id;


--
-- Name: api_keys; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.api_keys (
    id integer NOT NULL,
    key_hash character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    rate_limit_per_minute integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_used_at timestamp with time zone,
    created_by character varying(255)
);


ALTER TABLE public.api_keys OWNER TO dyn365hunter;

--
-- Name: api_keys_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.api_keys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_keys_id_seq OWNER TO dyn365hunter;

--
-- Name: api_keys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.api_keys_id_seq OWNED BY public.api_keys.id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.companies (
    id integer NOT NULL,
    canonical_name character varying(255) NOT NULL,
    domain character varying(255) NOT NULL,
    provider character varying(50),
    tenant_size character varying(50),
    country character varying(2),
    contact_emails jsonb,
    contact_quality_score integer,
    linkedin_pattern character varying(255),
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.companies OWNER TO dyn365hunter;

--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.companies_id_seq OWNER TO dyn365hunter;

--
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- Name: domain_signals; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.domain_signals (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    spf boolean,
    dkim boolean,
    dmarc_policy character varying(50),
    dmarc_coverage integer,
    mx_root character varying(255),
    local_provider character varying(255),
    registrar character varying(255),
    expires_at date,
    nameservers text[],
    scan_status character varying(50) NOT NULL,
    scanned_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.domain_signals OWNER TO dyn365hunter;

--
-- Name: domain_signals_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.domain_signals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domain_signals_id_seq OWNER TO dyn365hunter;

--
-- Name: domain_signals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.domain_signals_id_seq OWNED BY public.domain_signals.id;


--
-- Name: favorites; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.favorites (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    user_id character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.favorites OWNER TO dyn365hunter;

--
-- Name: favorites_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.favorites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.favorites_id_seq OWNER TO dyn365hunter;

--
-- Name: favorites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.favorites_id_seq OWNED BY public.favorites.id;


--
-- Name: ip_enrichment; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.ip_enrichment (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    ip_address character varying(45) NOT NULL,
    asn integer,
    asn_org character varying(255),
    isp character varying(255),
    country character varying(2),
    city character varying(255),
    usage_type character varying(32),
    is_proxy boolean,
    proxy_type character varying(32),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ip_enrichment OWNER TO dyn365hunter;

--
-- Name: ip_enrichment_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.ip_enrichment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ip_enrichment_id_seq OWNER TO dyn365hunter;

--
-- Name: ip_enrichment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.ip_enrichment_id_seq OWNED BY public.ip_enrichment.id;


--
-- Name: lead_scores; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.lead_scores (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    readiness_score integer NOT NULL,
    segment character varying(50) NOT NULL,
    reason text,
    technical_heat character varying(20),
    commercial_segment character varying(50),
    commercial_heat character varying(20),
    priority_category character varying(10),
    priority_label character varying(100),
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.lead_scores OWNER TO dyn365hunter;

--
-- Name: lead_scores_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.lead_scores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lead_scores_id_seq OWNER TO dyn365hunter;

--
-- Name: lead_scores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.lead_scores_id_seq OWNED BY public.lead_scores.id;


--
-- Name: leads_ready; Type: VIEW; Schema: public; Owner: dyn365hunter
--

CREATE VIEW public.leads_ready AS
 SELECT c.id AS company_id,
    c.canonical_name,
    c.domain,
    c.provider,
    c.tenant_size,
    c.country,
    c.contact_emails,
    c.contact_quality_score,
    c.linkedin_pattern,
    c.updated_at AS company_updated_at,
    ds.id AS signal_id,
    ds.spf,
    ds.dkim,
    ds.dmarc_policy,
    ds.dmarc_coverage,
    ds.mx_root,
    ds.local_provider,
    ds.registrar,
    ds.expires_at,
    ds.nameservers,
    ds.scan_status,
    ds.scanned_at,
    ls.id AS score_id,
    ls.readiness_score,
    ls.segment,
    ls.reason,
    ls.technical_heat,
    ls.commercial_segment,
    ls.commercial_heat,
    ls.priority_category,
    ls.priority_label
   FROM ((public.companies c
     LEFT JOIN public.domain_signals ds ON (((c.domain)::text = (ds.domain)::text)))
     LEFT JOIN public.lead_scores ls ON (((c.domain)::text = (ls.domain)::text)))
  WHERE (ls.readiness_score IS NOT NULL);


ALTER TABLE public.leads_ready OWNER TO dyn365hunter;

--
-- Name: notes; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.notes (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    note text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notes OWNER TO dyn365hunter;

--
-- Name: notes_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notes_id_seq OWNER TO dyn365hunter;

--
-- Name: notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.notes_id_seq OWNED BY public.notes.id;


--
-- Name: partner_center_referrals; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.partner_center_referrals (
    id integer NOT NULL,
    referral_id character varying(255) NOT NULL,
    referral_type character varying(50),
    company_name character varying(255),
    domain character varying(255),
    azure_tenant_id character varying(255),
    status character varying(50),
    raw_data jsonb,
    synced_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    engagement_id character varying(255),
    external_reference_id character varying(255),
    substatus character varying(50),
    type character varying(50),
    qualification character varying(50),
    direction character varying(50),
    customer_name character varying(255),
    customer_country character varying(100),
    deal_value numeric(15,2),
    currency character varying(10)
);


ALTER TABLE public.partner_center_referrals OWNER TO dyn365hunter;

--
-- Name: partner_center_referrals_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.partner_center_referrals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.partner_center_referrals_id_seq OWNER TO dyn365hunter;

--
-- Name: partner_center_referrals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.partner_center_referrals_id_seq OWNED BY public.partner_center_referrals.id;


--
-- Name: provider_change_history; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.provider_change_history (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    previous_provider character varying(50),
    new_provider character varying(50) NOT NULL,
    changed_at timestamp with time zone DEFAULT now() NOT NULL,
    scan_id integer
);


ALTER TABLE public.provider_change_history OWNER TO dyn365hunter;

--
-- Name: provider_change_history_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.provider_change_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.provider_change_history_id_seq OWNER TO dyn365hunter;

--
-- Name: provider_change_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.provider_change_history_id_seq OWNED BY public.provider_change_history.id;


--
-- Name: raw_leads; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.raw_leads (
    id integer NOT NULL,
    source character varying(50) NOT NULL,
    company_name character varying(255),
    email character varying(255),
    website character varying(255),
    domain character varying(255) NOT NULL,
    payload jsonb,
    ingested_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.raw_leads OWNER TO dyn365hunter;

--
-- Name: raw_leads_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.raw_leads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.raw_leads_id_seq OWNER TO dyn365hunter;

--
-- Name: raw_leads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.raw_leads_id_seq OWNED BY public.raw_leads.id;


--
-- Name: score_change_history; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.score_change_history (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    old_score integer,
    new_score integer,
    old_segment character varying(50),
    new_segment character varying(50),
    changed_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.score_change_history OWNER TO dyn365hunter;

--
-- Name: score_change_history_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.score_change_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.score_change_history_id_seq OWNER TO dyn365hunter;

--
-- Name: score_change_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.score_change_history_id_seq OWNED BY public.score_change_history.id;


--
-- Name: signal_change_history; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.signal_change_history (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    signal_type character varying(50) NOT NULL,
    old_value text,
    new_value text,
    changed_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.signal_change_history OWNER TO dyn365hunter;

--
-- Name: signal_change_history_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.signal_change_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.signal_change_history_id_seq OWNER TO dyn365hunter;

--
-- Name: signal_change_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.signal_change_history_id_seq OWNED BY public.signal_change_history.id;


--
-- Name: tags; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.tags (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    tag character varying(100) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tags OWNER TO dyn365hunter;

--
-- Name: tags_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tags_id_seq OWNER TO dyn365hunter;

--
-- Name: tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.tags_id_seq OWNED BY public.tags.id;


--
-- Name: webhook_retries; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.webhook_retries (
    id integer NOT NULL,
    api_key_id integer,
    payload jsonb NOT NULL,
    domain character varying(255),
    retry_count integer NOT NULL,
    max_retries integer NOT NULL,
    next_retry_at timestamp with time zone,
    status character varying(50) NOT NULL,
    error_message text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_retry_at timestamp with time zone
);


ALTER TABLE public.webhook_retries OWNER TO dyn365hunter;

--
-- Name: webhook_retries_id_seq; Type: SEQUENCE; Schema: public; Owner: dyn365hunter
--

CREATE SEQUENCE public.webhook_retries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.webhook_retries_id_seq OWNER TO dyn365hunter;

--
-- Name: webhook_retries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dyn365hunter
--

ALTER SEQUENCE public.webhook_retries_id_seq OWNED BY public.webhook_retries.id;


--
-- Name: alert_config id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.alert_config ALTER COLUMN id SET DEFAULT nextval('public.alert_config_id_seq'::regclass);


--
-- Name: alerts id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.alerts ALTER COLUMN id SET DEFAULT nextval('public.alerts_id_seq'::regclass);


--
-- Name: api_keys id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.api_keys ALTER COLUMN id SET DEFAULT nextval('public.api_keys_id_seq'::regclass);


--
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- Name: domain_signals id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.domain_signals ALTER COLUMN id SET DEFAULT nextval('public.domain_signals_id_seq'::regclass);


--
-- Name: favorites id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.favorites ALTER COLUMN id SET DEFAULT nextval('public.favorites_id_seq'::regclass);


--
-- Name: ip_enrichment id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.ip_enrichment ALTER COLUMN id SET DEFAULT nextval('public.ip_enrichment_id_seq'::regclass);


--
-- Name: lead_scores id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.lead_scores ALTER COLUMN id SET DEFAULT nextval('public.lead_scores_id_seq'::regclass);


--
-- Name: notes id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.notes ALTER COLUMN id SET DEFAULT nextval('public.notes_id_seq'::regclass);


--
-- Name: partner_center_referrals id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.partner_center_referrals ALTER COLUMN id SET DEFAULT nextval('public.partner_center_referrals_id_seq'::regclass);


--
-- Name: provider_change_history id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.provider_change_history ALTER COLUMN id SET DEFAULT nextval('public.provider_change_history_id_seq'::regclass);


--
-- Name: raw_leads id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.raw_leads ALTER COLUMN id SET DEFAULT nextval('public.raw_leads_id_seq'::regclass);


--
-- Name: score_change_history id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.score_change_history ALTER COLUMN id SET DEFAULT nextval('public.score_change_history_id_seq'::regclass);


--
-- Name: signal_change_history id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.signal_change_history ALTER COLUMN id SET DEFAULT nextval('public.signal_change_history_id_seq'::regclass);


--
-- Name: tags id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.tags ALTER COLUMN id SET DEFAULT nextval('public.tags_id_seq'::regclass);


--
-- Name: webhook_retries id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.webhook_retries ALTER COLUMN id SET DEFAULT nextval('public.webhook_retries_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.alembic_version (version_num) FROM stdin;
f972cf4c08f8
\.


--
-- Data for Name: alert_config; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.alert_config (id, user_id, alert_type, notification_method, enabled, frequency, webhook_url, email_address, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: alerts; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.alerts (id, domain, alert_type, alert_message, status, notification_method, sent_at, created_at) FROM stdin;
\.


--
-- Data for Name: api_keys; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.api_keys (id, key_hash, name, rate_limit_per_minute, is_active, created_at, last_used_at, created_by) FROM stdin;
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.companies (id, canonical_name, domain, provider, tenant_size, country, contact_emails, contact_quality_score, linkedin_pattern, updated_at) FROM stdin;
60	kartalrulman.com	kartalrulman.com	\N	\N	\N	\N	\N	\N	2025-11-18 08:12:09.1792+00
2	meptur.com	meptur.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:12:35.228175+00
61	kartalrulman.com.tr	kartalrulman.com.tr	M365	medium	\N	\N	\N	\N	2025-11-18 08:12:15.789183+00
1	Gibibyte	gibibyte.com.tr	M365	medium	\N	\N	\N	\N	2025-11-18 15:37:50.799511+00
86	uppoint	uppoint.com.tr	M365	medium	\N	\N	\N	\N	2025-11-18 15:40:06.172022+00
18	ERTUĞ METAL DÖKÜM MAKİNA SAN.VE TİC. A.Ş.	ertugmetal.com	M365	medium	\N	\N	\N	\N	2025-11-18 15:46:06.599428+00
29	KAMETSAN METAL İNŞAAT SAN.VE TİC.A.Ş.	kametsanmetal.com.tr	\N	\N	\N	\N	\N	\N	2025-11-17 20:13:27.158475+00
30	KAZIM YÜZGÜLLÜ	yuzgullu.com	\N	\N	\N	\N	\N	\N	2025-11-17 20:13:27.165982+00
42	ÜÇGE DRS DEPO RAF SİSTEMLERİ PAZARLAMA SAN.VE TİC.A.Ş.	ucge-drs.com	\N	\N	\N	\N	\N	\N	2025-11-17 20:13:27.262304+00
3	ABS GRUP BOYA VE KİMYA SAN.TİC.LTD.ŞTİ.	aydinboya.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
4	ACAR AKÜ MALZ.İÇ VE DIŞ TİC.LTD.ŞTİ.	acaraku.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
5	ALFATEKS TEKSTİL ÜRÜNLERİ MADENCİLİK SAN.VE TİC.A.Ş.	alfateks.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
6	AQUA ANA MEŞRUBAT A.Ş.	gumus.com.tr	Google	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
7	ARGOS DIŞ TİCARET LTD.ŞTİ.	argos.com.tr	Google	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
8	ASTEKNİK MAK.SAN.VE TİC.A.Ş.	asteknikvana.com	M365	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
9	ATILIM YEM TARIM NAK.HAYVANCILIK VE ÜRÜN.GIDA SAN.TİC.LTD.ŞTİ.	atilimyem.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
12	BİRCAN KİMYA PLASTİK SAN.VE TİC.A.Ş.	bircanplastik.com	Yandex	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
13	DARDAĞAN GIDA SAN.VE TİC.LTD.ŞTİ.	dardagangida.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
14	DİNK GIDA SAN.VE TİC.LTD.ŞTİ.	dinkgida.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
15	DIRAKMAN SÜTLÜ VE UNLU MAMÜLLER SAN.VE TİC.LTD.ŞTİ.	dirakman.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
17	ERALP MAKİNE KAZAN KİMYA VE EKİPMANLARI  SAN.VE TİC.LTD.ŞTİ.	eralpkazan.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
19	ERTUĞRUL HELVA TAHİN SUSAM GIDA İTHALAT İHRACAT SAN.VE TİC. LTD.ŞTİ.	ertugrulhelva.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
20	ERUSLU  SAĞLIK ÜRÜNLERİ SAN.VE TİC.A.Ş.	eruslusaglik.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
21	FİMAKS MAKİNA GIDA VE TARIM ÜRÜNLERİ SAN.TİC.A.Ş.	fimaks.com	M365	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
22	GLOBTEKS İPLİK SAN.TİC.LTD.ŞTİ.	globteks.com	Yandex	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
23	GÜRTAN PLASTİK SAN.VE TİC.LTD.ŞTİ.	gurtanplastik.com	Google	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
24	GÜVENAL TATLI SANAYİ VE TİCARET LİMİTED ŞİRKETİ	mkpguvenal.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
25	HARPUT TEKSTİL SANAYİ VE TİCARET A.Ş.-MİRANLI ŞUBE	harputtekstil.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
26	İĞREK MAKİNE SAN.VE TİC.A.Ş.	igrek.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
27	İNDO TEKSTİL VE DOKUMA SAN.TİC.A.Ş.	indotekstil.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
10	BARİT MADEN TÜRK A.Ş.	baritmaden.com	M365	medium	\N	\N	\N	\N	2025-11-17 21:46:10.820679+00
11	BATMAZ TEKSTİL SANAYİ VE  TİCARET LTD.ŞTİ.	batmaztekstil.com.tr	M365	medium	\N	\N	\N	\N	2025-11-17 22:00:02.384159+00
16	DM YAPI VE MADEN KİMYASALLARI KİMYEVİ  ÜRÜNLER İTHALAT İHR.TİC.VE SAN.LTD.ŞTİ.	dmkimya.com.tr	Google	large	\N	\N	\N	\N	2025-11-18 07:49:29.916924+00
28	İNTRO TARIM VE HAYVANCILIK A.Ş.	toruntex.com	Google	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
31	KIRAYTEKS TEKSTİL SAN.VE TİC.LTD.ŞTİ.	kirayteks.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
32	KOCAYUSUF AĞAÇ MAKİNALARI SANAYİ VE TİCARET LTD.ŞTİ.	kocayusufmakine.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
33	KSM METAL DÖVME MADENCİLİK İNŞ.SAN.TİC.LTD.ŞTİ.	celikdovme.com	Yandex	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
35	MİDOSER MODÜLER MOBİLYA İTH.İHR.SAN.VE TİC.LTD.ŞTİ.	midoser.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
36	MİRA ISI SİSTEMLERİ MÜHENDİSLİK SAN. ve TİC. LTD. ŞTİ.	miraheating.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
37	OTEGA TARIM HAYVANCILIK GIDA LOJİSTİK MAKİNE SAN.VE TİC.LTD.ŞTİ.	otega.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
38	ROLLPANEL YALITIM VE İNŞAAT MALZ.SAN.TİC.A.Ş.	rollmech.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
39	SEZER TARIM VE SAĞIM TEKN.SAN.TİC.LTD.ŞTİ. M.K.PAŞA ŞUBESİ	sezermac.com	Yandex	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
40	SİMETRİK PRO ÜRETİM SİSTEM ÇÖZ.VE END.EKİPM.TEK.SAN.VE TİC.LTD.ŞTİ.	simetrikpro.com	M365	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
41	TARIMSAL KİMYA TEK.SAN.VE TİC.A.Ş.	tarimsalkimya.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
43	ÜNALSAN METAL VE MAKİNA SAN.VE TİC.A.Ş.	unalsan.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
44	YÜREK TEKSTİL SANAYİ VE TİCARET A.Ş.	yurektekstil.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 20:13:27.897524+00
45	eralpkimya.com	eralpkimya.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:22:41.291983+00
46	eralpfintube.com	eralpfintube.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:36:44.359258+00
47	eralpsoftware.com	eralpsoftware.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:37:46.781711+00
48	eralprefinish.com	eralprefinish.com	Local	\N	\N	\N	\N	\N	2025-11-17 20:40:12.977116+00
34	MATLI YEM SANAYİİ VE TİCARET A.Ş.	matli.com.tr	M365	medium	\N	\N	\N	\N	2025-11-17 21:29:38.309147+00
49	plastay.com	plastay.com	M365	medium	\N	\N	\N	\N	2025-11-17 21:46:36.860373+00
50	geneks.com	geneks.com	M365	medium	\N	\N	\N	\N	2025-11-17 21:47:43.616017+00
51	royalmotors.com	royalmotors.com	Google	large	\N	\N	\N	\N	2025-11-17 21:48:41.4907+00
52	meptur.com.tr	meptur.com.tr	M365	medium	\N	\N	\N	\N	2025-11-17 21:49:03.305738+00
53	marvel.com.tr	marvel.com.tr	M365	medium	\N	\N	\N	\N	2025-11-17 21:49:10.162434+00
54	zerengroup.com	zerengroup.com	M365	medium	\N	\N	\N	\N	2025-11-17 21:49:46.009022+00
55	hekimoglu.com.yt	hekimoglu.com.yt	\N	\N	\N	\N	\N	\N	2025-11-17 21:50:54.047504+00
56	hekimoglu.com.tr	hekimoglu.com.tr	Google	large	\N	\N	\N	\N	2025-11-17 21:51:01.135679+00
57	hekimogludokum.com.tr	hekimogludokum.com.tr	Local	\N	\N	\N	\N	\N	2025-11-17 21:51:43.564049+00
58	hekimogludokum.com	hekimogludokum.com	M365	medium	\N	\N	\N	\N	2025-11-17 21:56:18.713016+00
59	kartalkimya.com	kartalkimya.com	M365	medium	\N	\N	\N	\N	2025-11-18 07:55:20.431242+00
\.


--
-- Data for Name: domain_signals; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.domain_signals (id, domain, spf, dkim, dmarc_policy, dmarc_coverage, mx_root, local_provider, registrar, expires_at, nameservers, scan_status, scanned_at) FROM stdin;
137	batmaztekstil.com.tr	t	f	\N	\N	outlook.com	\N	\N	\N	\N	completed	2025-11-18 15:55:33.259736+00
2	meptur.com	t	t	none	100	kriweb.com	Kriweb	Network Solutions, LLC	2025-12-16	{ns1.kriweb.com,ns2.kriweb.com}	completed	2025-11-17 20:12:35.906001+00
48	eralpkimya.com	t	f	\N	\N	vit.com.tr	VIT	IHS Telekom, Inc.	2025-12-04	{ns1.ulutek.net,ns2.ulutek.net}	completed	2025-11-17 20:22:43.295665+00
49	eralpfintube.com	t	f	\N	\N	eralpfintube.com	\N	IHS Telekom, Inc.	2026-03-12	{ns1.ulutek.net,ns2.ulutek.net}	completed	2025-11-17 20:36:47.113618+00
50	eralpsoftware.com	t	f	\N	\N	eralpsoftware.com	\N	IHS Telekom, Inc.	2026-07-22	{ns1.ulutek.net,ns2.ulutek.net}	completed	2025-11-17 20:37:49.259048+00
51	eralprefinish.com	t	f	\N	\N	vit.com.tr	VIT	IHS Telekom, Inc.	2026-04-26	{ns1.ulutek.net,ns2.ulutek.net}	completed	2025-11-17 20:40:15.251447+00
54	plastay.com	t	t	none	100	outlook.com	\N	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2026-03-13	{denver.ns.cloudflare.com,kiki.ns.cloudflare.com}	completed	2025-11-17 21:46:37.55521+00
58	marvel.com.tr	t	t	\N	\N	outlook.com	\N	\N	\N	\N	completed	2025-11-17 21:49:10.898349+00
55	geneks.com	t	t	\N	\N	outlook.com	\N	IHS Telekom, Inc.	2028-04-12	{bayan.ns.cloudflare.com,lorna.ns.cloudflare.com}	completed	2025-11-17 21:47:44.309948+00
56	royalmotors.com	t	f	\N	\N	google.com	\N	GoDaddy.com, LLC	2027-07-30	{pdns11.domaincontrol.com,pdns12.domaincontrol.com}	completed	2025-11-17 21:48:42.315643+00
57	meptur.com.tr	t	f	\N	\N	outlook.com	\N	\N	\N	\N	completed	2025-11-17 21:49:03.735069+00
59	zerengroup.com	t	t	quarantine	100	outlook.com	\N	Turkticaret.net Yazilim Hizmetleri Sanayi ve Ticaret A.S.	2026-10-01	{chad.ns.cloudflare.com,laylah.ns.cloudflare.com}	completed	2025-11-17 21:49:46.68737+00
61	hekimoglu.com.yt	f	f	\N	\N	\N	\N	\N	\N	\N	completed	2025-11-17 21:50:57.09321+00
62	hekimoglu.com.tr	t	f	quarantine	100	google.com	\N	\N	\N	\N	completed	2025-11-17 21:51:01.996363+00
63	hekimogludokum.com.tr	t	t	\N	\N	hekimogludokum.com.tr	\N	\N	\N	\N	completed	2025-11-17 21:51:44.06468+00
66	hekimogludokum.com	t	f	none	100	outlook.com	\N	IHS Telekom, Inc.	2026-01-11	{ns1.hostingpanel.com.tr,ns2.hostingpanel.com.tr}	completed	2025-11-17 22:01:31.707292+00
68	kartalkimya.com	t	f	\N	\N	outlook.com	\N	Nics Telekomunikasyon A.S.	2026-03-16	{jihoon.ns.cloudflare.com,stephane.ns.cloudflare.com}	completed	2025-11-18 07:55:21.581406+00
69	kartalrulman.com	f	f	\N	\N	\N	\N	OnlineNIC, Inc.	2028-01-31	{ns1.markum.net,ns2.markum.net}	completed	2025-11-18 08:12:09.211182+00
70	kartalrulman.com.tr	t	t	none	100	outlook.com	\N	\N	\N	\N	completed	2025-11-18 08:12:16.405525+00
90	gibibyte.com.tr	t	t	\N	\N	outlook.com	\N	\N	\N	\N	completed	2025-11-18 15:37:50.823499+00
91	uppoint.com.tr	t	t	reject	100	outlook.com	\N	\N	\N	\N	completed	2025-11-18 15:40:06.79705+00
94	aydinboya.com	t	t	none	100	pendns.net	Pendns	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2026-04-23	{ns1.fanaajans.com,ns2.fanaajans.com}	success	2025-11-18 15:51:01.733459+00
95	acaraku.com.tr	t	f	\N	\N	natrohost.com	Natro	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
96	alfateks.com.tr	t	f	none	100	alfateks.com.tr	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
97	gumus.com.tr	t	f	\N	\N	GOOGLE.COM	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
98	argos.com.tr	t	f	\N	\N	GOOGLE.COM	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
99	asteknikvana.com	t	t	reject	100	outlook.com	\N	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2026-01-17	{ns1.entetanitim.com,ns2.entetanitim.com}	success	2025-11-18 15:51:01.733459+00
100	atilimyem.com.tr	t	t	quarantine	100	atilimyem.com.tr	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
101	baritmaden.com	t	f	\N	\N	outlook.com	\N	Tucows Domains Inc.	2028-10-22	{hostdns1.doruk.net.tr,hostdns2.doruk.net.tr,hostdns3.doruk.net.tr}	success	2025-11-18 15:51:01.733459+00
103	bircanplastik.com	t	t	\N	\N	yandex.net	\N	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2026-01-21	{ns1.kggsoft.net,ns2.kggsoft.net}	success	2025-11-18 15:51:01.733459+00
104	dardagangida.com.tr	t	f	\N	\N	dardagangida.com.tr	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
105	dinkgida.com.tr	t	f	\N	\N	dinkgida.com.tr	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
106	dirakman.com	t	t	\N	\N	dirakman.com	\N	PDR Ltd. d/b/a PublicDomainRegistry.com	2026-12-19	{ns1.guzelhosting.com,ns11.guzelhosting.com,ns12.guzelhosting.com,ns2.guzelhosting.com}	success	2025-11-18 15:51:01.733459+00
108	eralpkazan.com	t	f	none	100	vit.com.tr	VIT	IHS Telekom, Inc.	2026-01-17	{ns1.ulutek.net,ns2.ulutek.net}	success	2025-11-18 15:51:01.733459+00
109	ertugmetal.com	t	f	\N	\N	outlook.com	\N	Nics Telekomunikasyon A.S.	2028-07-04	{ns1.natrohost.com,ns2.natrohost.com}	success	2025-11-18 15:51:01.733459+00
110	ertugrulhelva.com	t	f	\N	\N	natrohost.com	Natro	Nics Telekomunikasyon A.S.	2027-02-05	{ns1.natrohost.com,ns2.natrohost.com}	success	2025-11-18 15:51:01.733459+00
111	eruslusaglik.com.tr	t	t	none	100	trendmicro.eu	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
112	fimaks.com	t	t	none	100	outlook.com	\N	Nics Telekomunikasyon A.S.	2025-12-12	{ns1.natrohost.com,ns2.natrohost.com}	success	2025-11-18 15:51:01.733459+00
113	globteks.com	t	t	reject	100	yandex.net	\N	IHS Telekom, Inc.	2027-02-26	{ns1.ihsdnsx29.com,ns2.ihsdnsx29.com}	success	2025-11-18 15:51:01.733459+00
114	gurtanplastik.com	t	f	\N	\N	google.com	\N	Nics Telekomunikasyon A.S.	2026-06-13	{ns5.dnssaglayici.com,ns6.dnssaglayici.com}	success	2025-11-18 15:51:01.733459+00
115	mkpguvenal.com	t	f	\N	\N	mkpguvenal.com	\N	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2025-12-11	{bursa.profornet.net,merkez.profornet.net}	success	2025-11-18 15:51:01.733459+00
116	harputtekstil.com.tr	t	f	quarantine	100	harputholding.com.tr	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
117	igrek.com.tr	t	t	none	100	bulutino.com	Bulutino	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
118	indotekstil.com	t	t	none	100	kriweb.com	Kriweb	Atak Domain Bilgi Teknolojileri A.S.	2028-05-10	{ns1.kriweb.com,ns2.kriweb.com}	success	2025-11-18 15:51:01.733459+00
119	toruntex.com	t	f	\N	\N	google.com	\N	Cronon GmbH	2026-03-31	{ns12.wixdns.net,ns13.wixdns.net}	success	2025-11-18 15:51:01.733459+00
120	kametsanmetal.com.tr	f	f	\N	\N	\N	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
121	yuzgullu.com	f	f	\N	\N	\N	\N	GoDaddy.com, LLC	2026-04-07	{arely.ns.cloudflare.com,cosmin.ns.cloudflare.com}	success	2025-11-18 15:51:01.733459+00
122	kirayteks.com.tr	t	f	quarantine	100	trendmicro.eu	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
123	kocayusufmakine.com	t	t	none	100	mxrouting.net	\N	PDR Ltd. d/b/a PublicDomainRegistry.com	2029-03-28	{ns1.crewmedya.tr,ns2.crewmedya.tr}	success	2025-11-18 15:51:01.733459+00
124	celikdovme.com	t	f	\N	\N	yandex.net	\N	FBS Inc.	2026-03-08	{eu.dnsenable.com,tr.dnsenable.com,us.dnsenable.com}	success	2025-11-18 15:51:01.733459+00
125	matli.com.tr	t	f	reject	100	outlook.com	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
126	midoser.com	t	t	\N	\N	midoser.com	\N	Cizgi Telekomunikasyon A.S.	2030-04-06	{austin.ns.cloudflare.com,dayana.ns.cloudflare.com}	success	2025-11-18 15:51:01.733459+00
127	miraheating.com	t	f	\N	\N	miraheating.com	\N	PDR Ltd. d/b/a PublicDomainRegistry.com	2026-10-17	{ns1.wee22.com,ns2.wee22.com,ns3.wee22.com}	success	2025-11-18 15:51:01.733459+00
128	otega.com.tr	t	f	\N	\N	otega.com.tr	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
129	rollmech.com	t	f	\N	\N	ppe-hosted.com	\N	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2026-05-06	{dnx1.vodafone.net.tr,dnx2.vodafone.net.tr}	success	2025-11-18 15:51:01.733459+00
130	sezermac.com	t	f	none	100	yandex.net	\N	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2033-12-17	{vds5.armdns.com,vds6.armdns.com}	success	2025-11-18 15:51:01.733459+00
131	simetrikpro.com	t	f	none	100	outlook.com	\N	FBS Inc.	2026-06-10	{ns1.artiiki.com,ns2.artiiki.com}	success	2025-11-18 15:51:01.733459+00
132	tarimsalkimya.com.tr	t	t	quarantine	100	barracudanetworks.com	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
133	ucge-drs.com	f	f	\N	\N	\N	\N	Amazon Registrar, Inc.	2026-03-16	{ns1.tekkilavuz.com,ns2.tekkilavuz.com}	success	2025-11-18 15:51:01.733459+00
134	unalsan.com	t	f	reject	100	unalsan.com	\N	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2028-11-09	{dina.ns.cloudflare.com,rick.ns.cloudflare.com}	success	2025-11-18 15:51:01.733459+00
135	yurektekstil.com.tr	t	f	none	100	yurektekstil.com.tr	\N	\N	\N	\N	whois_failed	2025-11-18 15:51:01.733459+00
136	dmkimya.com.tr	t	t	\N	\N	GOOGLE.COM	\N	\N	\N	\N	completed	2025-11-18 15:52:12.635785+00
\.


--
-- Data for Name: favorites; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.favorites (id, domain, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: ip_enrichment; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.ip_enrichment (id, domain, ip_address, asn, asn_org, isp, country, city, usage_type, is_proxy, proxy_type, created_at, updated_at) FROM stdin;
1	gibibyte.com.tr	52.101.73.6	\N	\N	\N	NL	Amsterdam	\N	\N	\N	2025-11-17 19:53:18.413359+00	2025-11-17 19:53:18.413359+00
2	meptur.com	185.73.201.246	\N	\N	\N	TR	Istanbul	\N	\N	\N	2025-11-17 20:12:36.116845+00	2025-11-17 20:12:36.116845+00
3	acaraku.com.tr	94.73.183.142	\N	\N	\N	TR	\N	\N	\N	\N	2025-11-17 20:14:57.491441+00	2025-11-17 20:14:57.491441+00
4	celikdovme.com	77.88.21.249	\N	\N	\N	RU	\N	\N	\N	\N	2025-11-17 20:15:13.841129+00	2025-11-17 20:15:13.841129+00
5	eralpkazan.com	79.171.16.211	\N	\N	\N	TR	Gaziemir	\N	\N	\N	2025-11-17 20:18:14.775717+00	2025-11-17 20:18:14.775717+00
6	eralpkimya.com	79.171.17.150	\N	\N	\N	TR	Gaziemir	\N	\N	\N	2025-11-17 20:22:43.570737+00	2025-11-17 20:22:43.570737+00
7	eralpfintube.com	79.171.16.58	\N	\N	\N	TR	Gaziemir	\N	\N	\N	2025-11-17 20:36:47.427554+00	2025-11-17 20:36:47.427554+00
8	eralpsoftware.com	79.171.16.206	\N	\N	\N	TR	Gaziemir	\N	\N	\N	2025-11-17 20:37:50.6222+00	2025-11-17 20:37:50.6222+00
9	eralprefinish.com	188.124.24.137	\N	\N	\N	TR	Gebze	\N	\N	\N	2025-11-17 20:40:15.609666+00	2025-11-17 20:40:15.609666+00
10	matli.com.tr	52.101.73.4	\N	\N	\N	NL	Amsterdam	\N	\N	\N	2025-11-17 21:29:39.204185+00	2025-11-17 21:29:39.204185+00
11	baritmaden.com	52.101.68.32	\N	\N	\N	IE	Dublin	\N	\N	\N	2025-11-17 21:46:12.199078+00	2025-11-17 21:46:12.199078+00
12	plastay.com	52.101.73.26	\N	\N	\N	NL	Amsterdam	\N	\N	\N	2025-11-17 21:46:37.734676+00	2025-11-17 21:46:37.734676+00
13	geneks.com	52.101.68.32	\N	\N	\N	IE	Dublin	\N	\N	\N	2025-11-17 21:47:44.493322+00	2025-11-17 21:47:44.493322+00
14	royalmotors.com	142.251.173.26	\N	\N	\N	US	\N	\N	\N	\N	2025-11-17 21:48:42.787781+00	2025-11-17 21:48:42.787781+00
15	meptur.com.tr	52.101.73.11	\N	\N	\N	NL	Amsterdam	\N	\N	\N	2025-11-17 21:49:03.904928+00	2025-11-17 21:49:03.904928+00
16	marvel.com.tr	52.101.68.3	\N	\N	\N	IE	Dublin	\N	\N	\N	2025-11-17 21:49:11.107497+00	2025-11-17 21:49:11.107497+00
17	zerengroup.com	52.101.73.1	\N	\N	\N	NL	Amsterdam	\N	\N	\N	2025-11-17 21:49:47.073906+00	2025-11-17 21:49:47.073906+00
18	hekimoglu.com.tr	64.233.167.26	\N	\N	\N	US	\N	\N	\N	\N	2025-11-17 21:51:02.418629+00	2025-11-17 21:51:02.418629+00
19	hekimogludokum.com.tr	185.106.22.28	\N	\N	\N	TR	\N	\N	\N	\N	2025-11-17 21:51:44.168361+00	2025-11-17 21:51:44.168361+00
20	hekimogludokum.com	52.101.68.12	\N	\N	\N	IE	Dublin	\N	\N	\N	2025-11-17 21:56:19.882812+00	2025-11-17 21:56:19.882812+00
21	batmaztekstil.com.tr	52.101.73.15	\N	\N	\N	NL	Amsterdam	\N	\N	\N	2025-11-17 22:00:03.263866+00	2025-11-17 22:00:03.263866+00
22	hekimogludokum.com	52.101.73.30	\N	\N	\N	NL	Amsterdam	\N	\N	\N	2025-11-17 22:01:31.910253+00	2025-11-17 22:01:31.910253+00
23	dmkimya.com.tr	64.233.167.27	\N	\N	\N	US	\N	\N	\N	\N	2025-11-18 07:49:33.074423+00	2025-11-18 07:49:33.074423+00
24	kartalkimya.com	52.101.68.8	\N	\N	\N	IE	Dublin	\N	\N	\N	2025-11-18 07:55:21.791741+00	2025-11-18 07:55:21.791741+00
25	kartalrulman.com.tr	52.101.68.15	\N	\N	\N	IE	Dublin	\N	\N	\N	2025-11-18 08:12:16.591697+00	2025-11-18 08:12:16.591697+00
26	gibibyte.com.tr	52.101.73.30	\N	\N	\N	NL	Amsterdam	\N	\N	\N	2025-11-18 15:37:16.327039+00	2025-11-18 15:37:16.327039+00
27	gibibyte.com.tr	52.101.68.32	\N	\N	\N	IE	Dublin	\N	\N	\N	2025-11-18 15:37:50.992811+00	2025-11-18 15:37:50.992811+00
28	uppoint.com.tr	52.101.68.32	\N	\N	\N	IE	Dublin	\N	\N	\N	2025-11-18 15:40:06.971155+00	2025-11-18 15:40:06.971155+00
29	aydinboya.com	62.106.94.15	\N	\N	\N	TR	\N	\N	\N	\N	2025-11-18 15:45:10.787651+00	2025-11-18 15:45:10.787651+00
30	ertugmetal.com	52.101.68.3	\N	\N	\N	IE	Dublin	\N	\N	\N	2025-11-18 15:46:07.620888+00	2025-11-18 15:46:07.620888+00
31	dmkimya.com.tr	74.125.206.26	\N	\N	\N	US	\N	\N	\N	\N	2025-11-18 15:52:17.532102+00	2025-11-18 15:52:17.532102+00
32	batmaztekstil.com.tr	52.101.68.5	\N	\N	\N	IE	Dublin	\N	\N	\N	2025-11-18 15:55:33.45397+00	2025-11-18 15:55:33.45397+00
\.


--
-- Data for Name: lead_scores; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.lead_scores (id, domain, readiness_score, segment, reason, technical_heat, commercial_segment, commercial_heat, priority_category, priority_label, updated_at) FROM stdin;
137	batmaztekstil.com.tr	45	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 45, Provider: M365	Hot	WEAK_PARTNER	MEDIUM	P3	Existing Microsoft but Weak Partner	2025-11-18 15:55:33.259736+00
2	meptur.com	20	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 20, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-17 20:12:35.906001+00
48	eralpkimya.com	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-17 20:22:43.295665+00
49	eralpfintube.com	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-17 20:36:47.113618+00
50	eralpsoftware.com	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-17 20:37:49.259048+00
51	eralprefinish.com	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-17 20:40:15.251447+00
54	plastay.com	60	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 60, Provider: M365	Hot	WEAK_PARTNER	HIGH	P3	Existing Microsoft but Weak Partner	2025-11-17 21:46:37.55521+00
55	geneks.com	70	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 70, Provider: M365	Hot	RENEWAL	MEDIUM	P4	Renewal Pressure	2025-11-17 21:47:44.309948+00
56	royalmotors.com	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Google	Cold	LOW_INTENT	LOW	P5	Low Intent / Long Nurturing	2025-11-17 21:48:42.315643+00
57	meptur.com.tr	45	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 45, Provider: M365	Hot	WEAK_PARTNER	MEDIUM	P3	Existing Microsoft but Weak Partner	2025-11-17 21:49:03.735069+00
58	marvel.com.tr	70	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 70, Provider: M365	Hot	RENEWAL	MEDIUM	P4	Renewal Pressure	2025-11-17 21:49:10.898349+00
59	zerengroup.com	85	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 85, Provider: M365	Hot	RENEWAL	MEDIUM	P4	Renewal Pressure	2025-11-17 21:49:46.68737+00
61	hekimoglu.com.yt	0	Skip	Hard-fail: MX kaydı yok	\N	\N	\N	\N	\N	2025-11-17 21:50:57.09321+00
62	hekimoglu.com.tr	60	Migration	Cloud kullanıcıları, geçişe hazır. Score: 60, Provider: Google	Warm	COMPETITIVE	HIGH	P2	Competitive Takeover	2025-11-17 21:51:01.996363+00
63	hekimogludokum.com.tr	30	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 30, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-17 21:51:44.06468+00
66	hekimogludokum.com	35	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 35, Provider: M365	Hot	WEAK_PARTNER	MEDIUM	P3	Existing Microsoft but Weak Partner	2025-11-17 22:01:31.707292+00
68	kartalkimya.com	45	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 45, Provider: M365	Hot	WEAK_PARTNER	MEDIUM	P3	Existing Microsoft but Weak Partner	2025-11-18 07:55:21.581406+00
69	kartalrulman.com	0	Skip	Hard-fail: MX kaydı yok	\N	\N	\N	\N	\N	2025-11-18 08:12:09.211182+00
70	kartalrulman.com.tr	60	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 60, Provider: M365	Hot	WEAK_PARTNER	HIGH	P3	Existing Microsoft but Weak Partner	2025-11-18 08:12:16.405525+00
90	gibibyte.com.tr	70	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 70, Provider: M365	Hot	RENEWAL	MEDIUM	P4	Renewal Pressure	2025-11-18 15:37:50.823499+00
91	uppoint.com.tr	90	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 90, Provider: M365	Hot	RENEWAL	MEDIUM	P4	Renewal Pressure	2025-11-18 15:40:06.79705+00
94	aydinboya.com	20	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 20, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
95	acaraku.com.tr	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
96	alfateks.com.tr	0	Skip	Yetersiz veri, analiz dışı. Score: 0, Provider: Local	Cold	NO_GO	LOW	P6	No-Go / Archive	2025-11-18 15:51:01.733459+00
97	gumus.com.tr	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Google	Cold	LOW_INTENT	LOW	P5	Low Intent / Long Nurturing	2025-11-18 15:51:01.733459+00
98	argos.com.tr	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Google	Cold	LOW_INTENT	LOW	P5	Low Intent / Long Nurturing	2025-11-18 15:51:01.733459+00
99	asteknikvana.com	90	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 90, Provider: M365	Hot	RENEWAL	MEDIUM	P4	Renewal Pressure	2025-11-18 15:51:01.733459+00
100	atilimyem.com.tr	45	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 45, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
101	baritmaden.com	45	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 45, Provider: M365	Hot	WEAK_PARTNER	MEDIUM	P3	Existing Microsoft but Weak Partner	2025-11-18 15:51:01.733459+00
103	bircanplastik.com	50	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 50, Provider: Yandex	Cold	LOW_INTENT	LOW	P5	Low Intent / Long Nurturing	2025-11-18 15:51:01.733459+00
104	dardagangida.com.tr	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
105	dinkgida.com.tr	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
106	dirakman.com	30	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 30, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
108	eralpkazan.com	0	Skip	Yetersiz veri, analiz dışı. Score: 0, Provider: Local	Cold	NO_GO	LOW	P6	No-Go / Archive	2025-11-18 15:51:01.733459+00
109	ertugmetal.com	45	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 45, Provider: M365	Hot	WEAK_PARTNER	MEDIUM	P3	Existing Microsoft but Weak Partner	2025-11-18 15:51:01.733459+00
110	ertugrulhelva.com	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
111	eruslusaglik.com.tr	20	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 20, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
112	fimaks.com	60	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 60, Provider: M365	Hot	WEAK_PARTNER	HIGH	P3	Existing Microsoft but Weak Partner	2025-11-18 15:51:01.733459+00
113	globteks.com	70	Migration	Cloud kullanıcıları, geçişe hazır. Score: 70, Provider: Yandex	Warm	COMPETITIVE	HIGH	P2	Competitive Takeover	2025-11-18 15:51:01.733459+00
114	gurtanplastik.com	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Google	Cold	LOW_INTENT	LOW	P5	Low Intent / Long Nurturing	2025-11-18 15:51:01.733459+00
115	mkpguvenal.com	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
116	harputtekstil.com.tr	20	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 20, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
117	igrek.com.tr	20	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 20, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
118	indotekstil.com	20	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 20, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
119	toruntex.com	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Google	Cold	LOW_INTENT	LOW	P5	Low Intent / Long Nurturing	2025-11-18 15:51:01.733459+00
120	kametsanmetal.com.tr	0	Skip	Hard-fail: MX kaydı yok	\N	\N	\N	\N	\N	2025-11-18 15:51:01.733459+00
121	yuzgullu.com	0	Skip	Hard-fail: MX kaydı yok	\N	\N	\N	\N	\N	2025-11-18 15:51:01.733459+00
122	kirayteks.com.tr	20	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 20, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
123	kocayusufmakine.com	20	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 20, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
124	celikdovme.com	25	Skip	Yetersiz veri, analiz dışı. Score: 25, Provider: Yandex	Cold	NO_GO	LOW	P6	No-Go / Archive	2025-11-18 15:51:01.733459+00
125	matli.com.tr	65	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 65, Provider: M365	Hot	WEAK_PARTNER	HIGH	P3	Existing Microsoft but Weak Partner	2025-11-18 15:51:01.733459+00
126	midoser.com	30	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 30, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
127	miraheating.com	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
128	otega.com.tr	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
129	rollmech.com	5	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 5, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
130	sezermac.com	15	Skip	Yetersiz veri, analiz dışı. Score: 15, Provider: Yandex	Cold	NO_GO	LOW	P6	No-Go / Archive	2025-11-18 15:51:01.733459+00
131	simetrikpro.com	35	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 35, Provider: M365	Hot	WEAK_PARTNER	MEDIUM	P3	Existing Microsoft but Weak Partner	2025-11-18 15:51:01.733459+00
132	tarimsalkimya.com.tr	45	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 45, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
133	ucge-drs.com	0	Skip	Hard-fail: MX kaydı yok	\N	\N	\N	\N	\N	2025-11-18 15:51:01.733459+00
134	unalsan.com	25	Cold	Self-hosted mail sunucusu kullanıyor, M365'e migration potansiyeli var (düşük öncelik). Score: 25, Provider: Local	Cold	GREENFIELD	HIGH	P1	High Potential Greenfield	2025-11-18 15:51:01.733459+00
135	yurektekstil.com.tr	0	Skip	Yetersiz veri, analiz dışı. Score: 0, Provider: Local	Cold	NO_GO	LOW	P6	No-Go / Archive	2025-11-18 15:51:01.733459+00
136	dmkimya.com.tr	70	Migration	Cloud kullanıcıları, geçişe hazır. Score: 70, Provider: Google	Warm	COMPETITIVE	HIGH	P2	Competitive Takeover	2025-11-18 15:52:12.635785+00
\.


--
-- Data for Name: notes; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.notes (id, domain, note, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: partner_center_referrals; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.partner_center_referrals (id, referral_id, referral_type, company_name, domain, azure_tenant_id, status, raw_data, synced_at, created_at, updated_at, engagement_id, external_reference_id, substatus, type, qualification, direction, customer_name, customer_country, deal_value, currency) FROM stdin;
54	test-ref-001	co-sell	Test Company	dmkimya.com.tr	\N	Active	\N	2025-11-26 22:58:42.671209+00	2025-11-26 22:58:42.671209+00	2025-11-26 22:58:42.671209+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
55	test-ref-002	marketplace	Test Company 2	globteks.com	\N	Active	\N	2025-11-26 22:58:43.944776+00	2025-11-26 22:58:43.944776+00	2025-11-26 22:58:43.944776+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
56	test-ref-003	solution-provider	Test Company 3	asteknikvana.com	\N	Active	\N	2025-11-26 22:58:45.219533+00	2025-11-26 22:58:45.219533+00	2025-11-26 22:58:45.219533+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: provider_change_history; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.provider_change_history (id, domain, previous_provider, new_provider, changed_at, scan_id) FROM stdin;
\.


--
-- Data for Name: raw_leads; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.raw_leads (id, source, company_name, email, website, domain, payload, ingested_at) FROM stdin;
1	domain	\N	\N	\N	gibibyte.com.tr	{"email": null, "website": null, "original_domain": "gibibyte.com.tr"}	2025-11-17 19:53:17.694071+00
2	domain	\N	\N	\N	meptur.com	{"email": null, "website": null, "original_domain": "meptur.com"}	2025-11-17 20:12:35.208785+00
3	csv	ABS GRUP BOYA VE KİMYA SAN.TİC.LTD.ŞTİ.	\N	\N	aydinboya.com	{"email": null, "website": null, "row_index": 4, "original_domain": "https://www.aydinboya.com"}	2025-11-17 20:13:26.945732+00
4	csv	ACAR AKÜ MALZ.İÇ VE DIŞ TİC.LTD.ŞTİ.	\N	\N	acaraku.com.tr	{"email": null, "website": null, "row_index": 5, "original_domain": "http://www.acaraku.com.tr/"}	2025-11-17 20:13:26.953802+00
5	csv	ALFATEKS TEKSTİL ÜRÜNLERİ MADENCİLİK SAN.VE TİC.A.Ş.	\N	\N	alfateks.com.tr	{"email": null, "website": null, "row_index": 7, "original_domain": "http://www.alfateks.com.tr/"}	2025-11-17 20:13:26.960756+00
6	csv	AQUA ANA MEŞRUBAT A.Ş.	\N	\N	gumus.com.tr	{"email": null, "website": null, "row_index": 8, "original_domain": "https://www.gumus.com.tr/"}	2025-11-17 20:13:26.967454+00
7	csv	AQUA ANA MEŞRUBAT A.Ş.	\N	\N	gumus.com.tr	{"email": null, "website": null, "row_index": 9, "original_domain": "https://www.gumus.com.tr/"}	2025-11-17 20:13:26.977496+00
8	csv	ARGOS DIŞ TİCARET LTD.ŞTİ.	\N	\N	argos.com.tr	{"email": null, "website": null, "row_index": 10, "original_domain": "http://www.argos.com.tr/"}	2025-11-17 20:13:26.98635+00
9	csv	ASTEKNİK MAK.SAN.VE TİC.A.Ş.	\N	\N	asteknikvana.com	{"email": null, "website": null, "row_index": 11, "original_domain": "http://www.asteknikvana.com/"}	2025-11-17 20:13:26.99405+00
10	csv	ATILIM YEM TARIM NAK.HAYVANCILIK VE ÜRÜN.GIDA SAN.TİC.LTD.ŞTİ.	\N	\N	atilimyem.com.tr	{"email": null, "website": null, "row_index": 12, "original_domain": "http://atilimyem.com.tr/"}	2025-11-17 20:13:27.001275+00
11	csv	BARİT MADEN TÜRK A.Ş.	\N	\N	baritmaden.com	{"email": null, "website": null, "row_index": 13, "original_domain": "http://www.baritmaden.com/"}	2025-11-17 20:13:27.010702+00
12	csv	BATMAZ TEKSTİL SANAYİ VE  TİCARET LTD.ŞTİ.	\N	\N	batmaztekstil.com.tr	{"email": null, "website": null, "row_index": 14, "original_domain": "http://www.batmaztekstil.com.tr/"}	2025-11-17 20:13:27.01948+00
13	csv	BİRCAN KİMYA PLASTİK SAN.VE TİC.A.Ş.	\N	\N	bircanplastik.com	{"email": null, "website": null, "row_index": 15, "original_domain": "http://www.bircanplastik.com/"}	2025-11-17 20:13:27.026278+00
14	csv	DARDAĞAN GIDA SAN.VE TİC.LTD.ŞTİ.	\N	\N	dardagangida.com.tr	{"email": null, "website": null, "row_index": 17, "original_domain": "http://www.dardagangida.com.tr/"}	2025-11-17 20:13:27.03271+00
15	csv	DİNK GIDA SAN.VE TİC.LTD.ŞTİ.	\N	\N	dinkgida.com.tr	{"email": null, "website": null, "row_index": 19, "original_domain": "http://www.dinkgida.com.tr/"}	2025-11-17 20:13:27.043131+00
16	csv	DIRAKMAN SÜTLÜ VE UNLU MAMÜLLER SAN.VE TİC.LTD.ŞTİ.	\N	\N	dirakman.com	{"email": null, "website": null, "row_index": 20, "original_domain": "http://www.dirakman.com/"}	2025-11-17 20:13:27.051201+00
17	csv	DM YAPI VE MADEN KİMYASALLARI KİMYEVİ  ÜRÜNLER İTHALAT İHR.TİC.VE SAN.LTD.ŞTİ.	\N	\N	dmkimya.com.tr	{"email": null, "website": null, "row_index": 21, "original_domain": "http://www.dmkimya.com.tr/"}	2025-11-17 20:13:27.057746+00
18	csv	ERALP MAKİNE KAZAN KİMYA VE EKİPMANLARI  SAN.VE TİC.LTD.ŞTİ.	\N	\N	eralpkazan.com	{"email": null, "website": null, "row_index": 22, "original_domain": "http://www.eralpkazan.com/"}	2025-11-17 20:13:27.064199+00
19	csv	ERALP MAKİNE KAZAN KİMYA VE EKİPMANLARI  SAN.VE TİC.LTD.ŞTİ.	\N	\N	eralpkazan.com	{"email": null, "website": null, "row_index": 23, "original_domain": "http://www.eralpkazan.com/"}	2025-11-17 20:13:27.073975+00
20	csv	ERTUĞ METAL DÖKÜM MAKİNA SAN.VE TİC. A.Ş.	\N	\N	ertugmetal.com	{"email": null, "website": null, "row_index": 24, "original_domain": "http://www.ertugmetal.com/"}	2025-11-17 20:13:27.082068+00
21	csv	ERTUĞRUL HELVA TAHİN SUSAM GIDA İTHALAT İHRACAT SAN.VE TİC. LTD.ŞTİ.	\N	\N	ertugrulhelva.com	{"email": null, "website": null, "row_index": 25, "original_domain": "http://www.ertugrulhelva.com/"}	2025-11-17 20:13:27.088928+00
22	csv	ERUSLU  SAĞLIK ÜRÜNLERİ SAN.VE TİC.A.Ş.	\N	\N	eruslusaglik.com.tr	{"email": null, "website": null, "row_index": 26, "original_domain": "https://eruslusaglik.com.tr/"}	2025-11-17 20:13:27.095409+00
23	csv	FİMAKS MAKİNA GIDA VE TARIM ÜRÜNLERİ SAN.TİC.A.Ş.	\N	\N	fimaks.com	{"email": null, "website": null, "row_index": 27, "original_domain": "http://www.fimaks.com/"}	2025-11-17 20:13:27.103108+00
24	csv	GLOBTEKS İPLİK SAN.TİC.LTD.ŞTİ.	\N	\N	globteks.com	{"email": null, "website": null, "row_index": 28, "original_domain": "http://www.globteks.com/"}	2025-11-17 20:13:27.111286+00
25	csv	GÜRTAN PLASTİK SAN.VE TİC.LTD.ŞTİ.	\N	\N	gurtanplastik.com	{"email": null, "website": null, "row_index": 30, "original_domain": "http://www.gurtanplastik.com/"}	2025-11-17 20:13:27.117539+00
26	csv	GÜVENAL TATLI SANAYİ VE TİCARET LİMİTED ŞİRKETİ	\N	\N	mkpguvenal.com	{"email": null, "website": null, "row_index": 31, "original_domain": "http://www.mkpguvenal.com"}	2025-11-17 20:13:27.123665+00
27	csv	HARPUT TEKSTİL SANAYİ VE TİCARET A.Ş.-MİRANLI ŞUBE	\N	\N	harputtekstil.com.tr	{"email": null, "website": null, "row_index": 32, "original_domain": "http://www.harputtekstil.com.tr/"}	2025-11-17 20:13:27.129906+00
28	csv	İĞREK MAKİNE SAN.VE TİC.A.Ş.	\N	\N	igrek.com.tr	{"email": null, "website": null, "row_index": 33, "original_domain": "http://www.igrek.com.tr/"}	2025-11-17 20:13:27.139722+00
29	csv	İĞREK MAKİNE SAN.VE TİC.A.Ş.	\N	\N	igrek.com.tr	{"email": null, "website": null, "row_index": 34, "original_domain": "http://www.igrek.com.tr/"}	2025-11-17 20:13:27.145812+00
30	csv	İNDO TEKSTİL VE DOKUMA SAN.TİC.A.Ş.	\N	\N	indotekstil.com	{"email": null, "website": null, "row_index": 35, "original_domain": "http://www.indotekstil.com/"}	2025-11-17 20:13:27.152205+00
31	csv	İNTRO TARIM VE HAYVANCILIK A.Ş.	\N	\N	toruntex.com	{"email": null, "website": null, "row_index": 36, "original_domain": "https://www.toruntex.com/"}	2025-11-17 20:13:27.158475+00
32	csv	KAMETSAN METAL İNŞAAT SAN.VE TİC.A.Ş.	\N	\N	kametsanmetal.com.tr	{"email": null, "website": null, "row_index": 37, "original_domain": "www.kametsanmetal.com.tr"}	2025-11-17 20:13:27.165982+00
33	csv	KAZIM YÜZGÜLLÜ	\N	\N	yuzgullu.com	{"email": null, "website": null, "row_index": 38, "original_domain": "http://yuzgullu.com/"}	2025-11-17 20:13:27.172902+00
34	csv	KIRAYTEKS TEKSTİL SAN.VE TİC.LTD.ŞTİ.	\N	\N	kirayteks.com.tr	{"email": null, "website": null, "row_index": 39, "original_domain": "http://kirayteks.com.tr/"}	2025-11-17 20:13:27.180022+00
35	csv	KOCAYUSUF AĞAÇ MAKİNALARI SANAYİ VE TİCARET LTD.ŞTİ.	\N	\N	kocayusufmakine.com	{"email": null, "website": null, "row_index": 40, "original_domain": "http://www.kocayusufmakine.com"}	2025-11-17 20:13:27.187557+00
36	csv	KSM METAL DÖVME MADENCİLİK İNŞ.SAN.TİC.LTD.ŞTİ.	\N	\N	celikdovme.com	{"email": null, "website": null, "row_index": 41, "original_domain": "http://www.celikdovme.com/"}	2025-11-17 20:13:27.196652+00
37	csv	MATLI YEM SANAYİİ VE TİCARET A.Ş.	\N	\N	matli.com.tr	{"email": null, "website": null, "row_index": 43, "original_domain": "http://www.matli.com.tr/"}	2025-11-17 20:13:27.203339+00
38	csv	MİDOSER MODÜLER MOBİLYA İTH.İHR.SAN.VE TİC.LTD.ŞTİ.	\N	\N	midoser.com	{"email": null, "website": null, "row_index": 45, "original_domain": "https://midoser.com/"}	2025-11-17 20:13:27.209753+00
39	csv	MİRA ISI SİSTEMLERİ MÜHENDİSLİK SAN. ve TİC. LTD. ŞTİ.	\N	\N	miraheating.com	{"email": null, "website": null, "row_index": 46, "original_domain": "http://www.miraheating.com/"}	2025-11-17 20:13:27.215819+00
40	csv	OTEGA TARIM HAYVANCILIK GIDA LOJİSTİK MAKİNE SAN.VE TİC.LTD.ŞTİ.	\N	\N	otega.com.tr	{"email": null, "website": null, "row_index": 49, "original_domain": "http://www.otega.com.tr/"}	2025-11-17 20:13:27.22582+00
41	csv	ROLLPANEL YALITIM VE İNŞAAT MALZ.SAN.TİC.A.Ş.	\N	\N	rollmech.com	{"email": null, "website": null, "row_index": 52, "original_domain": "http://www.rollmech.com/"}	2025-11-17 20:13:27.233499+00
42	csv	SEZER TARIM VE SAĞIM TEKN.SAN.TİC.LTD.ŞTİ. M.K.PAŞA ŞUBESİ	\N	\N	sezermac.com	{"email": null, "website": null, "row_index": 53, "original_domain": "http://www.sezermac.com/"}	2025-11-17 20:13:27.240176+00
43	csv	SİMETRİK PRO ÜRETİM SİSTEM ÇÖZ.VE END.EKİPM.TEK.SAN.VE TİC.LTD.ŞTİ.	\N	\N	simetrikpro.com	{"email": null, "website": null, "row_index": 54, "original_domain": "https://www.simetrikpro.com/"}	2025-11-17 20:13:27.247317+00
44	csv	TARIMSAL KİMYA TEK.SAN.VE TİC.A.Ş.	\N	\N	tarimsalkimya.com.tr	{"email": null, "website": null, "row_index": 56, "original_domain": "http://www.tarimsalkimya.com.tr/"}	2025-11-17 20:13:27.253884+00
45	csv	TARIMSAL KİMYA TEK.SAN.VE TİC.A.Ş.	\N	\N	tarimsalkimya.com.tr	{"email": null, "website": null, "row_index": 57, "original_domain": "http://www.tarimsalkimya.com.tr/"}	2025-11-17 20:13:27.262304+00
46	csv	ÜÇGE DRS DEPO RAF SİSTEMLERİ PAZARLAMA SAN.VE TİC.A.Ş.	\N	\N	ucge-drs.com	{"email": null, "website": null, "row_index": 58, "original_domain": "http://www.ucge-drs.com"}	2025-11-17 20:13:27.269117+00
47	csv	ÜNALSAN METAL VE MAKİNA SAN.VE TİC.A.Ş.	\N	\N	unalsan.com	{"email": null, "website": null, "row_index": 59, "original_domain": "https://unalsan.com/"}	2025-11-17 20:13:27.277073+00
48	csv	YÜREK TEKSTİL SANAYİ VE TİCARET A.Ş.	\N	\N	yurektekstil.com.tr	{"email": null, "website": null, "row_index": 61, "original_domain": "http://www.yurektekstil.com.tr/"}	2025-11-17 20:13:27.283998+00
49	domain	\N	\N	\N	eralpkimya.com	{"email": null, "website": null, "original_domain": "eralpkimya.com"}	2025-11-17 20:22:41.271133+00
50	domain	\N	\N	\N	eralpfintube.com	{"email": null, "website": null, "original_domain": "eralpfintube.com"}	2025-11-17 20:36:44.342757+00
51	domain	\N	\N	\N	eralpsoftware.com	{"email": null, "website": null, "original_domain": "eralpsoftware.com"}	2025-11-17 20:37:46.767909+00
52	domain	\N	\N	\N	eralprefinish.com	{"email": null, "website": null, "original_domain": "eralprefinish.com"}	2025-11-17 20:40:12.958319+00
53	domain	\N	\N	\N	plastay.com	{"email": null, "website": null, "original_domain": "plastay.com"}	2025-11-17 21:46:36.838495+00
54	domain	\N	\N	\N	geneks.com	{"email": null, "website": null, "original_domain": "geneks.com"}	2025-11-17 21:47:43.600568+00
55	domain	\N	\N	\N	royalmotors.com	{"email": null, "website": null, "original_domain": "royalmotors.com"}	2025-11-17 21:48:41.475971+00
56	domain	\N	\N	\N	meptur.com.tr	{"email": null, "website": null, "original_domain": "meptur.com.tr"}	2025-11-17 21:49:03.291966+00
57	domain	\N	\N	\N	marvel.com.tr	{"email": null, "website": null, "original_domain": "marvel.com.tr"}	2025-11-17 21:49:10.146797+00
58	domain	\N	\N	\N	zerengroup.com	{"email": null, "website": null, "original_domain": "zerengroup.com"}	2025-11-17 21:49:45.991133+00
59	domain	\N	\N	\N	hekimoglu.com.yt	{"email": null, "website": null, "original_domain": "hekimoglu.com.yt"}	2025-11-17 21:50:54.058141+00
60	domain	\N	\N	\N	hekimoglu.com.yt	{"email": null, "website": null, "original_domain": "hekimoglu.com.yt"}	2025-11-17 21:50:57.074829+00
61	domain	\N	\N	\N	hekimoglu.com.tr	{"email": null, "website": null, "original_domain": "hekimoglu.com.tr"}	2025-11-17 21:51:01.120771+00
62	domain	\N	\N	\N	hekimogludokum.com.tr	{"email": null, "website": null, "original_domain": "hekimogludokum.com.tr"}	2025-11-17 21:51:43.545992+00
63	domain	\N	\N	\N	hekimogludokum.com	{"email": null, "website": null, "original_domain": "hekimogludokum.com"}	2025-11-17 21:56:18.697546+00
64	domain	\N	\N	\N	hekimogludokum.com	{"email": null, "website": null, "original_domain": "hekimogludokum.com"}	2025-11-17 22:01:31.3982+00
65	domain	\N	\N	\N	kartalkimya.com	{"email": null, "website": null, "original_domain": "kartalkimya.com"}	2025-11-18 07:55:20.412211+00
66	domain	\N	\N	\N	kartalrulman.com	{"email": null, "website": null, "original_domain": "kartalrulman.com"}	2025-11-18 08:12:09.193676+00
67	domain	\N	\N	\N	kartalrulman.com.tr	{"email": null, "website": null, "original_domain": "kartalrulman.com.tr"}	2025-11-18 08:12:15.775322+00
74	domain	\N	\N	\N	gibibyte.com.tr	{"email": null, "website": null, "original_domain": "gibibyte.com.tr"}	2025-11-18 15:37:15.500436+00
75	domain	Gibibyte	\N	\N	gibibyte.com.tr	{"email": null, "website": null, "original_domain": "gibibyte.com.tr"}	2025-11-18 15:37:50.806811+00
76	domain	uppoint	\N	\N	uppoint.com.tr	{"email": null, "website": null, "original_domain": "uppoint.com.tr"}	2025-11-18 15:40:06.15738+00
77	csv	ABS GRUP BOYA VE KİMYA SAN.TİC.LTD.ŞTİ.	\N	\N	aydinboya.com	{"email": null, "website": null, "row_index": 4, "original_domain": "https://www.aydinboya.com"}	2025-11-18 15:51:01.054443+00
78	csv	ACAR AKÜ MALZ.İÇ VE DIŞ TİC.LTD.ŞTİ.	\N	\N	acaraku.com.tr	{"email": null, "website": null, "row_index": 5, "original_domain": "http://www.acaraku.com.tr/"}	2025-11-18 15:51:01.061141+00
79	csv	ALFATEKS TEKSTİL ÜRÜNLERİ MADENCİLİK SAN.VE TİC.A.Ş.	\N	\N	alfateks.com.tr	{"email": null, "website": null, "row_index": 7, "original_domain": "http://www.alfateks.com.tr/"}	2025-11-18 15:51:01.067023+00
80	csv	AQUA ANA MEŞRUBAT A.Ş.	\N	\N	gumus.com.tr	{"email": null, "website": null, "row_index": 8, "original_domain": "https://www.gumus.com.tr/"}	2025-11-18 15:51:01.074339+00
81	csv	AQUA ANA MEŞRUBAT A.Ş.	\N	\N	gumus.com.tr	{"email": null, "website": null, "row_index": 9, "original_domain": "https://www.gumus.com.tr/"}	2025-11-18 15:51:01.082861+00
82	csv	ARGOS DIŞ TİCARET LTD.ŞTİ.	\N	\N	argos.com.tr	{"email": null, "website": null, "row_index": 10, "original_domain": "http://www.argos.com.tr/"}	2025-11-18 15:51:01.089337+00
83	csv	ASTEKNİK MAK.SAN.VE TİC.A.Ş.	\N	\N	asteknikvana.com	{"email": null, "website": null, "row_index": 11, "original_domain": "http://www.asteknikvana.com/"}	2025-11-18 15:51:01.095674+00
84	csv	ATILIM YEM TARIM NAK.HAYVANCILIK VE ÜRÜN.GIDA SAN.TİC.LTD.ŞTİ.	\N	\N	atilimyem.com.tr	{"email": null, "website": null, "row_index": 12, "original_domain": "http://atilimyem.com.tr/"}	2025-11-18 15:51:01.102733+00
85	csv	BARİT MADEN TÜRK A.Ş.	\N	\N	baritmaden.com	{"email": null, "website": null, "row_index": 13, "original_domain": "http://www.baritmaden.com/"}	2025-11-18 15:51:01.109293+00
86	csv	BATMAZ TEKSTİL SANAYİ VE  TİCARET LTD.ŞTİ.	\N	\N	batmaztekstil.com.tr	{"email": null, "website": null, "row_index": 14, "original_domain": "http://www.batmaztekstil.com.tr/"}	2025-11-18 15:51:01.117128+00
87	csv	BİRCAN KİMYA PLASTİK SAN.VE TİC.A.Ş.	\N	\N	bircanplastik.com	{"email": null, "website": null, "row_index": 15, "original_domain": "http://www.bircanplastik.com/"}	2025-11-18 15:51:01.126009+00
88	csv	DARDAĞAN GIDA SAN.VE TİC.LTD.ŞTİ.	\N	\N	dardagangida.com.tr	{"email": null, "website": null, "row_index": 17, "original_domain": "http://www.dardagangida.com.tr/"}	2025-11-18 15:51:01.132453+00
89	csv	DİNK GIDA SAN.VE TİC.LTD.ŞTİ.	\N	\N	dinkgida.com.tr	{"email": null, "website": null, "row_index": 19, "original_domain": "http://www.dinkgida.com.tr/"}	2025-11-18 15:51:01.138613+00
90	csv	DIRAKMAN SÜTLÜ VE UNLU MAMÜLLER SAN.VE TİC.LTD.ŞTİ.	\N	\N	dirakman.com	{"email": null, "website": null, "row_index": 20, "original_domain": "http://www.dirakman.com/"}	2025-11-18 15:51:01.146399+00
91	csv	DM YAPI VE MADEN KİMYASALLARI KİMYEVİ  ÜRÜNLER İTHALAT İHR.TİC.VE SAN.LTD.ŞTİ.	\N	\N	dmkimya.com.tr	{"email": null, "website": null, "row_index": 21, "original_domain": "http://www.dmkimya.com.tr/"}	2025-11-18 15:51:01.154036+00
92	csv	ERALP MAKİNE KAZAN KİMYA VE EKİPMANLARI  SAN.VE TİC.LTD.ŞTİ.	\N	\N	eralpkazan.com	{"email": null, "website": null, "row_index": 22, "original_domain": "http://www.eralpkazan.com/"}	2025-11-18 15:51:01.160418+00
93	csv	ERALP MAKİNE KAZAN KİMYA VE EKİPMANLARI  SAN.VE TİC.LTD.ŞTİ.	\N	\N	eralpkazan.com	{"email": null, "website": null, "row_index": 23, "original_domain": "http://www.eralpkazan.com/"}	2025-11-18 15:51:01.167195+00
94	csv	ERTUĞ METAL DÖKÜM MAKİNA SAN.VE TİC. A.Ş.	\N	\N	ertugmetal.com	{"email": null, "website": null, "row_index": 24, "original_domain": "http://www.ertugmetal.com/"}	2025-11-18 15:51:01.176699+00
95	csv	ERTUĞRUL HELVA TAHİN SUSAM GIDA İTHALAT İHRACAT SAN.VE TİC. LTD.ŞTİ.	\N	\N	ertugrulhelva.com	{"email": null, "website": null, "row_index": 25, "original_domain": "http://www.ertugrulhelva.com/"}	2025-11-18 15:51:01.185162+00
96	csv	ERUSLU  SAĞLIK ÜRÜNLERİ SAN.VE TİC.A.Ş.	\N	\N	eruslusaglik.com.tr	{"email": null, "website": null, "row_index": 26, "original_domain": "https://eruslusaglik.com.tr/"}	2025-11-18 15:51:01.191722+00
97	csv	FİMAKS MAKİNA GIDA VE TARIM ÜRÜNLERİ SAN.TİC.A.Ş.	\N	\N	fimaks.com	{"email": null, "website": null, "row_index": 27, "original_domain": "http://www.fimaks.com/"}	2025-11-18 15:51:01.198712+00
98	csv	GLOBTEKS İPLİK SAN.TİC.LTD.ŞTİ.	\N	\N	globteks.com	{"email": null, "website": null, "row_index": 28, "original_domain": "http://www.globteks.com/"}	2025-11-18 15:51:01.204554+00
99	csv	GÜRTAN PLASTİK SAN.VE TİC.LTD.ŞTİ.	\N	\N	gurtanplastik.com	{"email": null, "website": null, "row_index": 30, "original_domain": "http://www.gurtanplastik.com/"}	2025-11-18 15:51:01.214787+00
100	csv	GÜVENAL TATLI SANAYİ VE TİCARET LİMİTED ŞİRKETİ	\N	\N	mkpguvenal.com	{"email": null, "website": null, "row_index": 31, "original_domain": "http://www.mkpguvenal.com"}	2025-11-18 15:51:01.221408+00
101	csv	HARPUT TEKSTİL SANAYİ VE TİCARET A.Ş.-MİRANLI ŞUBE	\N	\N	harputtekstil.com.tr	{"email": null, "website": null, "row_index": 32, "original_domain": "http://www.harputtekstil.com.tr/"}	2025-11-18 15:51:01.227706+00
102	csv	İĞREK MAKİNE SAN.VE TİC.A.Ş.	\N	\N	igrek.com.tr	{"email": null, "website": null, "row_index": 33, "original_domain": "http://www.igrek.com.tr/"}	2025-11-18 15:51:01.234152+00
103	csv	İĞREK MAKİNE SAN.VE TİC.A.Ş.	\N	\N	igrek.com.tr	{"email": null, "website": null, "row_index": 34, "original_domain": "http://www.igrek.com.tr/"}	2025-11-18 15:51:01.241726+00
104	csv	İNDO TEKSTİL VE DOKUMA SAN.TİC.A.Ş.	\N	\N	indotekstil.com	{"email": null, "website": null, "row_index": 35, "original_domain": "http://www.indotekstil.com/"}	2025-11-18 15:51:01.250058+00
105	csv	İNTRO TARIM VE HAYVANCILIK A.Ş.	\N	\N	toruntex.com	{"email": null, "website": null, "row_index": 36, "original_domain": "https://www.toruntex.com/"}	2025-11-18 15:51:01.256066+00
106	csv	KAMETSAN METAL İNŞAAT SAN.VE TİC.A.Ş.	\N	\N	kametsanmetal.com.tr	{"email": null, "website": null, "row_index": 37, "original_domain": "www.kametsanmetal.com.tr"}	2025-11-18 15:51:01.262453+00
107	csv	KAZIM YÜZGÜLLÜ	\N	\N	yuzgullu.com	{"email": null, "website": null, "row_index": 38, "original_domain": "http://yuzgullu.com/"}	2025-11-18 15:51:01.269625+00
108	csv	KIRAYTEKS TEKSTİL SAN.VE TİC.LTD.ŞTİ.	\N	\N	kirayteks.com.tr	{"email": null, "website": null, "row_index": 39, "original_domain": "http://kirayteks.com.tr/"}	2025-11-18 15:51:01.277003+00
109	csv	KOCAYUSUF AĞAÇ MAKİNALARI SANAYİ VE TİCARET LTD.ŞTİ.	\N	\N	kocayusufmakine.com	{"email": null, "website": null, "row_index": 40, "original_domain": "http://www.kocayusufmakine.com"}	2025-11-18 15:51:01.283374+00
110	csv	KSM METAL DÖVME MADENCİLİK İNŞ.SAN.TİC.LTD.ŞTİ.	\N	\N	celikdovme.com	{"email": null, "website": null, "row_index": 41, "original_domain": "http://www.celikdovme.com/"}	2025-11-18 15:51:01.289439+00
111	csv	MATLI YEM SANAYİİ VE TİCARET A.Ş.	\N	\N	matli.com.tr	{"email": null, "website": null, "row_index": 43, "original_domain": "http://www.matli.com.tr/"}	2025-11-18 15:51:01.296693+00
112	csv	MİDOSER MODÜLER MOBİLYA İTH.İHR.SAN.VE TİC.LTD.ŞTİ.	\N	\N	midoser.com	{"email": null, "website": null, "row_index": 45, "original_domain": "https://midoser.com/"}	2025-11-18 15:51:01.303098+00
113	csv	MİRA ISI SİSTEMLERİ MÜHENDİSLİK SAN. ve TİC. LTD. ŞTİ.	\N	\N	miraheating.com	{"email": null, "website": null, "row_index": 46, "original_domain": "http://www.miraheating.com/"}	2025-11-18 15:51:01.312056+00
114	csv	OTEGA TARIM HAYVANCILIK GIDA LOJİSTİK MAKİNE SAN.VE TİC.LTD.ŞTİ.	\N	\N	otega.com.tr	{"email": null, "website": null, "row_index": 49, "original_domain": "http://www.otega.com.tr/"}	2025-11-18 15:51:01.318633+00
115	csv	ROLLPANEL YALITIM VE İNŞAAT MALZ.SAN.TİC.A.Ş.	\N	\N	rollmech.com	{"email": null, "website": null, "row_index": 52, "original_domain": "http://www.rollmech.com/"}	2025-11-18 15:51:01.325862+00
116	csv	SEZER TARIM VE SAĞIM TEKN.SAN.TİC.LTD.ŞTİ. M.K.PAŞA ŞUBESİ	\N	\N	sezermac.com	{"email": null, "website": null, "row_index": 53, "original_domain": "http://www.sezermac.com/"}	2025-11-18 15:51:01.332155+00
117	csv	SİMETRİK PRO ÜRETİM SİSTEM ÇÖZ.VE END.EKİPM.TEK.SAN.VE TİC.LTD.ŞTİ.	\N	\N	simetrikpro.com	{"email": null, "website": null, "row_index": 54, "original_domain": "https://www.simetrikpro.com/"}	2025-11-18 15:51:01.339168+00
118	csv	TARIMSAL KİMYA TEK.SAN.VE TİC.A.Ş.	\N	\N	tarimsalkimya.com.tr	{"email": null, "website": null, "row_index": 56, "original_domain": "http://www.tarimsalkimya.com.tr/"}	2025-11-18 15:51:01.346007+00
119	csv	TARIMSAL KİMYA TEK.SAN.VE TİC.A.Ş.	\N	\N	tarimsalkimya.com.tr	{"email": null, "website": null, "row_index": 57, "original_domain": "http://www.tarimsalkimya.com.tr/"}	2025-11-18 15:51:01.352875+00
120	csv	ÜÇGE DRS DEPO RAF SİSTEMLERİ PAZARLAMA SAN.VE TİC.A.Ş.	\N	\N	ucge-drs.com	{"email": null, "website": null, "row_index": 58, "original_domain": "http://www.ucge-drs.com"}	2025-11-18 15:51:01.359082+00
121	csv	ÜNALSAN METAL VE MAKİNA SAN.VE TİC.A.Ş.	\N	\N	unalsan.com	{"email": null, "website": null, "row_index": 59, "original_domain": "https://unalsan.com/"}	2025-11-18 15:51:01.365655+00
122	csv	YÜREK TEKSTİL SANAYİ VE TİCARET A.Ş.	\N	\N	yurektekstil.com.tr	{"email": null, "website": null, "row_index": 61, "original_domain": "http://www.yurektekstil.com.tr/"}	2025-11-18 15:51:01.37291+00
\.


--
-- Data for Name: score_change_history; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.score_change_history (id, domain, old_score, new_score, old_segment, new_segment, changed_at) FROM stdin;
\.


--
-- Data for Name: signal_change_history; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.signal_change_history (id, domain, signal_type, old_value, new_value, changed_at) FROM stdin;
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.tags (id, domain, tag, created_at) FROM stdin;
1	meptur.com	expire-soon	2025-11-17 20:12:35.922684+00
2	meptur.com	weak-spf	2025-11-17 20:12:35.922684+00
3	meptur.com	local-mx	2025-11-17 20:12:35.922684+00
4	acaraku.com.tr	local-mx	2025-11-17 20:14:57.267838+00
5	eralpkazan.com	weak-spf	2025-11-17 20:18:14.43043+00
6	eralpkazan.com	local-mx	2025-11-17 20:18:14.43043+00
7	eralpkimya.com	expire-soon	2025-11-17 20:22:43.306743+00
8	eralpkimya.com	local-mx	2025-11-17 20:22:43.306743+00
9	eralpfintube.com	local-mx	2025-11-17 20:36:47.121901+00
10	eralpsoftware.com	local-mx	2025-11-17 20:37:49.266873+00
11	eralprefinish.com	local-mx	2025-11-17 20:40:15.26045+00
12	plastay.com	weak-spf	2025-11-17 21:46:37.562114+00
13	royalmotors.com	google-workspace	2025-11-17 21:48:42.322233+00
14	hekimoglu.com.yt	security-risk	2025-11-17 21:50:54.992059+00
15	hekimoglu.com.tr	migration-ready	2025-11-17 21:51:02.003332+00
16	hekimoglu.com.tr	google-workspace	2025-11-17 21:51:02.003332+00
17	hekimogludokum.com.tr	local-mx	2025-11-17 21:51:44.072318+00
18	hekimogludokum.com	weak-spf	2025-11-17 21:56:19.676045+00
19	dmkimya.com.tr	migration-ready	2025-11-18 07:49:32.607815+00
20	dmkimya.com.tr	google-workspace	2025-11-18 07:49:32.607815+00
21	kartalrulman.com	security-risk	2025-11-18 08:12:10.365595+00
22	kartalrulman.com.tr	weak-spf	2025-11-18 08:12:16.411785+00
23	aydinboya.com	weak-spf	2025-11-18 15:45:10.608053+00
24	aydinboya.com	local-mx	2025-11-18 15:45:10.608053+00
\.


--
-- Data for Name: webhook_retries; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.webhook_retries (id, api_key_id, payload, domain, retry_count, max_retries, next_retry_at, status, error_message, created_at, last_retry_at) FROM stdin;
\.


--
-- Name: alert_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.alert_config_id_seq', 1, false);


--
-- Name: alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.alerts_id_seq', 1, false);


--
-- Name: api_keys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.api_keys_id_seq', 1, false);


--
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.companies_id_seq', 86, true);


--
-- Name: domain_signals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.domain_signals_id_seq', 137, true);


--
-- Name: favorites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.favorites_id_seq', 1, false);


--
-- Name: ip_enrichment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.ip_enrichment_id_seq', 32, true);


--
-- Name: lead_scores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.lead_scores_id_seq', 137, true);


--
-- Name: notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.notes_id_seq', 1, false);


--
-- Name: partner_center_referrals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.partner_center_referrals_id_seq', 56, true);


--
-- Name: provider_change_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.provider_change_history_id_seq', 1, false);


--
-- Name: raw_leads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.raw_leads_id_seq', 151, true);


--
-- Name: score_change_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.score_change_history_id_seq', 1, false);


--
-- Name: signal_change_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.signal_change_history_id_seq', 1, false);


--
-- Name: tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.tags_id_seq', 24, true);


--
-- Name: webhook_retries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.webhook_retries_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: alert_config alert_config_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.alert_config
    ADD CONSTRAINT alert_config_pkey PRIMARY KEY (id);


--
-- Name: alerts alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);


--
-- Name: api_keys api_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: domain_signals domain_signals_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.domain_signals
    ADD CONSTRAINT domain_signals_pkey PRIMARY KEY (id);


--
-- Name: favorites favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_pkey PRIMARY KEY (id);


--
-- Name: ip_enrichment ip_enrichment_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.ip_enrichment
    ADD CONSTRAINT ip_enrichment_pkey PRIMARY KEY (id);


--
-- Name: lead_scores lead_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.lead_scores
    ADD CONSTRAINT lead_scores_pkey PRIMARY KEY (id);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (id);


--
-- Name: partner_center_referrals partner_center_referrals_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.partner_center_referrals
    ADD CONSTRAINT partner_center_referrals_pkey PRIMARY KEY (id);


--
-- Name: provider_change_history provider_change_history_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.provider_change_history
    ADD CONSTRAINT provider_change_history_pkey PRIMARY KEY (id);


--
-- Name: raw_leads raw_leads_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.raw_leads
    ADD CONSTRAINT raw_leads_pkey PRIMARY KEY (id);


--
-- Name: score_change_history score_change_history_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.score_change_history
    ADD CONSTRAINT score_change_history_pkey PRIMARY KEY (id);


--
-- Name: signal_change_history signal_change_history_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.signal_change_history
    ADD CONSTRAINT signal_change_history_pkey PRIMARY KEY (id);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: ip_enrichment uq_ip_enrichment_domain_ip; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.ip_enrichment
    ADD CONSTRAINT uq_ip_enrichment_domain_ip UNIQUE (domain, ip_address);


--
-- Name: webhook_retries webhook_retries_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.webhook_retries
    ADD CONSTRAINT webhook_retries_pkey PRIMARY KEY (id);


--
-- Name: idx_ip_enrichment_ip; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_ip_enrichment_ip ON public.ip_enrichment USING btree (ip_address);


--
-- Name: idx_partner_center_referrals_direction; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_partner_center_referrals_direction ON public.partner_center_referrals USING btree (direction);


--
-- Name: idx_partner_center_referrals_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_partner_center_referrals_domain ON public.partner_center_referrals USING btree (domain);


--
-- Name: idx_partner_center_referrals_status; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_partner_center_referrals_status ON public.partner_center_referrals USING btree (status);


--
-- Name: idx_partner_center_referrals_substatus; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_partner_center_referrals_substatus ON public.partner_center_referrals USING btree (substatus);


--
-- Name: idx_partner_center_referrals_synced_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_partner_center_referrals_synced_at ON public.partner_center_referrals USING btree (synced_at);


--
-- Name: idx_partner_center_referrals_tenant_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_partner_center_referrals_tenant_id ON public.partner_center_referrals USING btree (azure_tenant_id);


--
-- Name: idx_partner_center_referrals_type; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_partner_center_referrals_type ON public.partner_center_referrals USING btree (referral_type);


--
-- Name: ix_alert_config_alert_type; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_alert_config_alert_type ON public.alert_config USING btree (alert_type);


--
-- Name: ix_alert_config_enabled; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_alert_config_enabled ON public.alert_config USING btree (enabled);


--
-- Name: ix_alert_config_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_alert_config_id ON public.alert_config USING btree (id);


--
-- Name: ix_alert_config_user_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_alert_config_user_id ON public.alert_config USING btree (user_id);


--
-- Name: ix_alerts_alert_type; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_alerts_alert_type ON public.alerts USING btree (alert_type);


--
-- Name: ix_alerts_created_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_alerts_created_at ON public.alerts USING btree (created_at);


--
-- Name: ix_alerts_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_alerts_domain ON public.alerts USING btree (domain);


--
-- Name: ix_alerts_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_alerts_id ON public.alerts USING btree (id);


--
-- Name: ix_alerts_status; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_alerts_status ON public.alerts USING btree (status);


--
-- Name: ix_api_keys_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_api_keys_id ON public.api_keys USING btree (id);


--
-- Name: ix_api_keys_is_active; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_api_keys_is_active ON public.api_keys USING btree (is_active);


--
-- Name: ix_api_keys_key_hash; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE UNIQUE INDEX ix_api_keys_key_hash ON public.api_keys USING btree (key_hash);


--
-- Name: ix_api_keys_last_used_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_api_keys_last_used_at ON public.api_keys USING btree (last_used_at);


--
-- Name: ix_companies_contact_quality_score; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_companies_contact_quality_score ON public.companies USING btree (contact_quality_score);


--
-- Name: ix_companies_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE UNIQUE INDEX ix_companies_domain ON public.companies USING btree (domain);


--
-- Name: ix_companies_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_companies_id ON public.companies USING btree (id);


--
-- Name: ix_companies_provider; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_companies_provider ON public.companies USING btree (provider);


--
-- Name: ix_companies_tenant_size; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_companies_tenant_size ON public.companies USING btree (tenant_size);


--
-- Name: ix_companies_updated_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_companies_updated_at ON public.companies USING btree (updated_at);


--
-- Name: ix_domain_signals_dmarc_coverage; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_domain_signals_dmarc_coverage ON public.domain_signals USING btree (dmarc_coverage);


--
-- Name: ix_domain_signals_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_domain_signals_domain ON public.domain_signals USING btree (domain);


--
-- Name: ix_domain_signals_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_domain_signals_id ON public.domain_signals USING btree (id);


--
-- Name: ix_domain_signals_local_provider; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_domain_signals_local_provider ON public.domain_signals USING btree (local_provider);


--
-- Name: ix_domain_signals_mx_root; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_domain_signals_mx_root ON public.domain_signals USING btree (mx_root);


--
-- Name: ix_domain_signals_scan_status; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_domain_signals_scan_status ON public.domain_signals USING btree (scan_status);


--
-- Name: ix_domain_signals_scanned_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_domain_signals_scanned_at ON public.domain_signals USING btree (scanned_at);


--
-- Name: ix_favorites_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_favorites_domain ON public.favorites USING btree (domain);


--
-- Name: ix_favorites_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_favorites_id ON public.favorites USING btree (id);


--
-- Name: ix_favorites_user_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_favorites_user_id ON public.favorites USING btree (user_id);


--
-- Name: ix_ip_enrichment_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_ip_enrichment_domain ON public.ip_enrichment USING btree (domain);


--
-- Name: ix_ip_enrichment_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_ip_enrichment_id ON public.ip_enrichment USING btree (id);


--
-- Name: ix_lead_scores_commercial_heat; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_lead_scores_commercial_heat ON public.lead_scores USING btree (commercial_heat);


--
-- Name: ix_lead_scores_commercial_segment; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_lead_scores_commercial_segment ON public.lead_scores USING btree (commercial_segment);


--
-- Name: ix_lead_scores_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_lead_scores_domain ON public.lead_scores USING btree (domain);


--
-- Name: ix_lead_scores_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_lead_scores_id ON public.lead_scores USING btree (id);


--
-- Name: ix_lead_scores_priority_category; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_lead_scores_priority_category ON public.lead_scores USING btree (priority_category);


--
-- Name: ix_lead_scores_readiness_score; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_lead_scores_readiness_score ON public.lead_scores USING btree (readiness_score);


--
-- Name: ix_lead_scores_segment; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_lead_scores_segment ON public.lead_scores USING btree (segment);


--
-- Name: ix_lead_scores_technical_heat; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_lead_scores_technical_heat ON public.lead_scores USING btree (technical_heat);


--
-- Name: ix_lead_scores_updated_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_lead_scores_updated_at ON public.lead_scores USING btree (updated_at);


--
-- Name: ix_notes_created_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_notes_created_at ON public.notes USING btree (created_at);


--
-- Name: ix_notes_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_notes_domain ON public.notes USING btree (domain);


--
-- Name: ix_notes_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_notes_id ON public.notes USING btree (id);


--
-- Name: ix_partner_center_referrals_azure_tenant_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_partner_center_referrals_azure_tenant_id ON public.partner_center_referrals USING btree (azure_tenant_id);


--
-- Name: ix_partner_center_referrals_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_partner_center_referrals_domain ON public.partner_center_referrals USING btree (domain);


--
-- Name: ix_partner_center_referrals_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_partner_center_referrals_id ON public.partner_center_referrals USING btree (id);


--
-- Name: ix_partner_center_referrals_referral_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE UNIQUE INDEX ix_partner_center_referrals_referral_id ON public.partner_center_referrals USING btree (referral_id);


--
-- Name: ix_partner_center_referrals_referral_type; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_partner_center_referrals_referral_type ON public.partner_center_referrals USING btree (referral_type);


--
-- Name: ix_partner_center_referrals_status; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_partner_center_referrals_status ON public.partner_center_referrals USING btree (status);


--
-- Name: ix_partner_center_referrals_synced_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_partner_center_referrals_synced_at ON public.partner_center_referrals USING btree (synced_at);


--
-- Name: ix_provider_change_history_changed_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_provider_change_history_changed_at ON public.provider_change_history USING btree (changed_at);


--
-- Name: ix_provider_change_history_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_provider_change_history_domain ON public.provider_change_history USING btree (domain);


--
-- Name: ix_provider_change_history_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_provider_change_history_id ON public.provider_change_history USING btree (id);


--
-- Name: ix_raw_leads_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_raw_leads_domain ON public.raw_leads USING btree (domain);


--
-- Name: ix_raw_leads_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_raw_leads_id ON public.raw_leads USING btree (id);


--
-- Name: ix_raw_leads_source; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_raw_leads_source ON public.raw_leads USING btree (source);


--
-- Name: ix_score_change_history_changed_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_score_change_history_changed_at ON public.score_change_history USING btree (changed_at);


--
-- Name: ix_score_change_history_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_score_change_history_domain ON public.score_change_history USING btree (domain);


--
-- Name: ix_score_change_history_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_score_change_history_id ON public.score_change_history USING btree (id);


--
-- Name: ix_signal_change_history_changed_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_signal_change_history_changed_at ON public.signal_change_history USING btree (changed_at);


--
-- Name: ix_signal_change_history_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_signal_change_history_domain ON public.signal_change_history USING btree (domain);


--
-- Name: ix_signal_change_history_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_signal_change_history_id ON public.signal_change_history USING btree (id);


--
-- Name: ix_signal_change_history_signal_type; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_signal_change_history_signal_type ON public.signal_change_history USING btree (signal_type);


--
-- Name: ix_tags_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_tags_domain ON public.tags USING btree (domain);


--
-- Name: ix_tags_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_tags_id ON public.tags USING btree (id);


--
-- Name: ix_webhook_retries_api_key_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_webhook_retries_api_key_id ON public.webhook_retries USING btree (api_key_id);


--
-- Name: ix_webhook_retries_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_webhook_retries_domain ON public.webhook_retries USING btree (domain);


--
-- Name: ix_webhook_retries_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_webhook_retries_id ON public.webhook_retries USING btree (id);


--
-- Name: ix_webhook_retries_next_retry_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_webhook_retries_next_retry_at ON public.webhook_retries USING btree (next_retry_at);


--
-- Name: ix_webhook_retries_status; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX ix_webhook_retries_status ON public.webhook_retries USING btree (status);


--
-- Name: alerts alerts_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: domain_signals domain_signals_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.domain_signals
    ADD CONSTRAINT domain_signals_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: favorites favorites_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: ip_enrichment ip_enrichment_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.ip_enrichment
    ADD CONSTRAINT ip_enrichment_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: lead_scores lead_scores_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.lead_scores
    ADD CONSTRAINT lead_scores_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: notes notes_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: provider_change_history provider_change_history_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.provider_change_history
    ADD CONSTRAINT provider_change_history_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: score_change_history score_change_history_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.score_change_history
    ADD CONSTRAINT score_change_history_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: signal_change_history signal_change_history_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.signal_change_history
    ADD CONSTRAINT signal_change_history_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: tags tags_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: webhook_retries webhook_retries_api_key_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.webhook_retries
    ADD CONSTRAINT webhook_retries_api_key_id_fkey FOREIGN KEY (api_key_id) REFERENCES public.api_keys(id) ON DELETE SET NULL;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: dyn365hunter
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict VARZgznU9LU69WWxQSQ7qhOvWVdULvhVyp1LmbkLcI4pA3l4edhswBQOnQ1ptVa

