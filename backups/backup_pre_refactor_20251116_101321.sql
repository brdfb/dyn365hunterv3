--
-- PostgreSQL database dump
--

\restrict E0qu0MYNbUrhaXQaLlE18E1hg0dFf6m2oqoWB7gSorlGLbDwUEyZMjhDXfm06SB

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
-- Name: api_keys; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.api_keys (
    id integer NOT NULL,
    key_hash character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    rate_limit_per_minute integer DEFAULT 60,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    last_used_at timestamp with time zone,
    created_by character varying(255)
);


ALTER TABLE public.api_keys OWNER TO dyn365hunter;

--
-- Name: TABLE api_keys; Type: COMMENT; Schema: public; Owner: dyn365hunter
--

COMMENT ON TABLE public.api_keys IS 'API keys for webhook authentication (G16)';


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
    country character varying(2),
    contact_emails jsonb,
    contact_quality_score integer,
    linkedin_pattern character varying(255),
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_size character varying(50)
);


ALTER TABLE public.companies OWNER TO dyn365hunter;

--
-- Name: TABLE companies; Type: COMMENT; Schema: public; Owner: dyn365hunter
--

COMMENT ON TABLE public.companies IS 'Normalized company information with unique domain constraint';


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
    mx_root character varying(255),
    registrar character varying(255),
    expires_at date,
    nameservers text[],
    scan_status character varying(50) DEFAULT 'pending'::character varying,
    scanned_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    local_provider character varying(255),
    dmarc_coverage integer
);


ALTER TABLE public.domain_signals OWNER TO dyn365hunter;

--
-- Name: TABLE domain_signals; Type: COMMENT; Schema: public; Owner: dyn365hunter
--

COMMENT ON TABLE public.domain_signals IS 'DNS and WHOIS analysis results for domains';


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
-- Name: lead_scores; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.lead_scores (
    id integer NOT NULL,
    domain character varying(255) NOT NULL,
    readiness_score integer NOT NULL,
    segment character varying(50) NOT NULL,
    reason text,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.lead_scores OWNER TO dyn365hunter;

--
-- Name: TABLE lead_scores; Type: COMMENT; Schema: public; Owner: dyn365hunter
--

COMMENT ON TABLE public.lead_scores IS 'Calculated readiness scores and segments for domains';


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
    ls.updated_at AS score_updated_at
   FROM ((public.companies c
     LEFT JOIN public.domain_signals ds ON (((c.domain)::text = (ds.domain)::text)))
     LEFT JOIN public.lead_scores ls ON (((c.domain)::text = (ls.domain)::text)));


ALTER TABLE public.leads_ready OWNER TO dyn365hunter;

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
    ingested_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.raw_leads OWNER TO dyn365hunter;

--
-- Name: TABLE raw_leads; Type: COMMENT; Schema: public; Owner: dyn365hunter
--

COMMENT ON TABLE public.raw_leads IS 'Raw ingested data from various sources';


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
-- Name: webhook_retries; Type: TABLE; Schema: public; Owner: dyn365hunter
--

CREATE TABLE public.webhook_retries (
    id integer NOT NULL,
    api_key_id integer,
    payload jsonb NOT NULL,
    domain character varying(255),
    retry_count integer DEFAULT 0,
    max_retries integer DEFAULT 3,
    next_retry_at timestamp with time zone,
    status character varying(50) DEFAULT 'pending'::character varying,
    error_message text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    last_retry_at timestamp with time zone
);


ALTER TABLE public.webhook_retries OWNER TO dyn365hunter;

--
-- Name: TABLE webhook_retries; Type: COMMENT; Schema: public; Owner: dyn365hunter
--

COMMENT ON TABLE public.webhook_retries IS 'Failed webhook requests for retry with exponential backoff (G16)';


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
-- Name: lead_scores id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.lead_scores ALTER COLUMN id SET DEFAULT nextval('public.lead_scores_id_seq'::regclass);


--
-- Name: raw_leads id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.raw_leads ALTER COLUMN id SET DEFAULT nextval('public.raw_leads_id_seq'::regclass);


--
-- Name: webhook_retries id; Type: DEFAULT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.webhook_retries ALTER COLUMN id SET DEFAULT nextval('public.webhook_retries_id_seq'::regclass);


--
-- Data for Name: api_keys; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.api_keys (id, key_hash, name, rate_limit_per_minute, is_active, created_at, last_used_at, created_by) FROM stdin;
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.companies (id, canonical_name, domain, provider, country, contact_emails, contact_quality_score, linkedin_pattern, updated_at, tenant_size) FROM stdin;
1	example.com	example.com	\N	\N	\N	\N	\N	2025-11-15 20:49:43.303126+00	\N
2	Test Inc	test.com	\N	\N	\N	\N	\N	2025-11-15 20:54:17.37558+00	\N
4	gibibyte	gibibyte.com.tr	M365	\N	\N	\N	\N	2025-11-15 21:05:50.168832+00	medium
3	meptur	meptur.com.tr	M365	\N	\N	\N	\N	2025-11-15 21:06:22.007817+00	medium
31	KAMETSAN METAL İNŞAAT SAN.VE TİC.A.Ş.	kametsanmetal.com.tr	\N	\N	\N	\N	\N	2025-11-15 21:08:50.092643+00	\N
32	KAZIM YÜZGÜLLÜ	yuzgullu.com	\N	\N	\N	\N	\N	2025-11-15 21:08:50.100066+00	\N
44	ÜÇGE DRS DEPO RAF SİSTEMLERİ PAZARLAMA SAN.VE TİC.A.Ş.	ucge-drs.com	\N	\N	\N	\N	\N	2025-11-15 21:08:50.211375+00	\N
5	ABS GRUP BOYA VE KİMYA SAN.TİC.LTD.ŞTİ.	aydinboya.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
6	ACAR AKÜ MALZ.İÇ VE DIŞ TİC.LTD.ŞTİ.	acaraku.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
7	ALFATEKS TEKSTİL ÜRÜNLERİ MADENCİLİK SAN.VE TİC.A.Ş.	alfateks.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
8	AQUA ANA MEŞRUBAT A.Ş.	gumus.com.tr	Google	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
11	ATILIM YEM TARIM NAK.HAYVANCILIK VE ÜRÜN.GIDA SAN.TİC.LTD.ŞTİ.	atilimyem.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
12	BARİT MADEN TÜRK A.Ş.	baritmaden.com	M365	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
13	BATMAZ TEKSTİL SANAYİ VE  TİCARET LTD.ŞTİ.	batmaztekstil.com.tr	M365	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
14	BİRCAN KİMYA PLASTİK SAN.VE TİC.A.Ş.	bircanplastik.com	Yandex	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
15	DARDAĞAN GIDA SAN.VE TİC.LTD.ŞTİ.	dardagangida.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
16	DİNK GIDA SAN.VE TİC.LTD.ŞTİ.	dinkgida.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
17	DIRAKMAN SÜTLÜ VE UNLU MAMÜLLER SAN.VE TİC.LTD.ŞTİ.	dirakman.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
19	ERALP MAKİNE KAZAN KİMYA VE EKİPMANLARI  SAN.VE TİC.LTD.ŞTİ.	eralpkazan.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
20	ERTUĞ METAL DÖKÜM MAKİNA SAN.VE TİC. A.Ş.	ertugmetal.com	M365	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
21	ERTUĞRUL HELVA TAHİN SUSAM GIDA İTHALAT İHRACAT SAN.VE TİC. LTD.ŞTİ.	ertugrulhelva.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
22	ERUSLU  SAĞLIK ÜRÜNLERİ SAN.VE TİC.A.Ş.	eruslusaglik.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
23	FİMAKS MAKİNA GIDA VE TARIM ÜRÜNLERİ SAN.TİC.A.Ş.	fimaks.com	M365	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
24	GLOBTEKS İPLİK SAN.TİC.LTD.ŞTİ.	globteks.com	Yandex	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
25	GÜRTAN PLASTİK SAN.VE TİC.LTD.ŞTİ.	gurtanplastik.com	Google	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
26	GÜVENAL TATLI SANAYİ VE TİCARET LİMİTED ŞİRKETİ	mkpguvenal.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
27	HARPUT TEKSTİL SANAYİ VE TİCARET A.Ş.-MİRANLI ŞUBE	harputtekstil.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
28	İĞREK MAKİNE SAN.VE TİC.A.Ş.	igrek.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
10	ASTEKNİK MAK.SAN.VE TİC.A.Ş.	asteknikvana.com	M365	\N	\N	\N	\N	2025-11-15 21:10:51.801142+00	medium
18	DM YAPI VE MADEN KİMYASALLARI KİMYEVİ  ÜRÜNLER İTHALAT İHR.TİC.VE SAN.LTD.ŞTİ.	dmkimya.com.tr	Google	\N	\N	\N	\N	2025-11-15 21:11:25.300819+00	large
9	ARGOS DIŞ TİCARET LTD.ŞTİ.	argos.com.tr	Google	\N	\N	\N	\N	2025-11-15 21:13:30.000542+00	large
29	İNDO TEKSTİL VE DOKUMA SAN.TİC.A.Ş.	indotekstil.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
30	İNTRO TARIM VE HAYVANCILIK A.Ş.	toruntex.com	Google	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
33	KIRAYTEKS TEKSTİL SAN.VE TİC.LTD.ŞTİ.	kirayteks.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
34	KOCAYUSUF AĞAÇ MAKİNALARI SANAYİ VE TİCARET LTD.ŞTİ.	kocayusufmakine.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
35	KSM METAL DÖVME MADENCİLİK İNŞ.SAN.TİC.LTD.ŞTİ.	celikdovme.com	Yandex	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
37	MİDOSER MODÜLER MOBİLYA İTH.İHR.SAN.VE TİC.LTD.ŞTİ.	midoser.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
38	MİRA ISI SİSTEMLERİ MÜHENDİSLİK SAN. ve TİC. LTD. ŞTİ.	miraheating.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
39	OTEGA TARIM HAYVANCILIK GIDA LOJİSTİK MAKİNE SAN.VE TİC.LTD.ŞTİ.	otega.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
40	ROLLPANEL YALITIM VE İNŞAAT MALZ.SAN.TİC.A.Ş.	rollmech.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
41	SEZER TARIM VE SAĞIM TEKN.SAN.TİC.LTD.ŞTİ. M.K.PAŞA ŞUBESİ	sezermac.com	Yandex	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
42	SİMETRİK PRO ÜRETİM SİSTEM ÇÖZ.VE END.EKİPM.TEK.SAN.VE TİC.LTD.ŞTİ.	simetrikpro.com	M365	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
43	TARIMSAL KİMYA TEK.SAN.VE TİC.A.Ş.	tarimsalkimya.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
45	ÜNALSAN METAL VE MAKİNA SAN.VE TİC.A.Ş.	unalsan.com	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
46	YÜREK TEKSTİL SANAYİ VE TİCARET A.Ş.	yurektekstil.com.tr	Local	\N	\N	\N	\N	2025-11-15 21:08:51.066602+00	\N
36	MATLI YEM SANAYİİ VE TİCARET A.Ş.	matli.com.tr	M365	\N	\N	\N	\N	2025-11-15 21:12:31.151247+00	medium
\.


--
-- Data for Name: domain_signals; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.domain_signals (id, domain, spf, dkim, dmarc_policy, mx_root, registrar, expires_at, nameservers, scan_status, scanned_at, local_provider, dmarc_coverage) FROM stdin;
1	example.com	t	t	reject	\N	RESERVED-Internet Assigned Numbers Authority	2026-08-13	{a.iana-servers.net,b.iana-servers.net}	completed	2025-11-15 20:49:43.354589+00	\N	\N
2	test.com	f	f	\N	\N	Network Solutions, LLC	2027-06-17	{ns1.safesecureweb.com,ns2.safesecureweb.com,ns3.safesecureweb.com}	completed	2025-11-15 20:54:17.150663+00	\N	\N
5	gibibyte.com.tr	t	t	none	outlook.com	\N	\N	\N	completed	2025-11-15 21:05:50.192447+00	\N	100
6	meptur.com.tr	t	f	\N	outlook.com	\N	\N	\N	completed	2025-11-15 21:06:22.016821+00	\N	100
7	aydinboya.com	t	t	none	pendns.net	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2026-04-23	{ns1.fanaajans.com,ns2.fanaajans.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
8	acaraku.com.tr	t	f	\N	natrohost.com	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
9	alfateks.com.tr	t	f	none	alfateks.com.tr	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
10	gumus.com.tr	t	f	\N	GOOGLE.COM	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
11	gumus.com.tr	t	f	\N	GOOGLE.COM	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
15	baritmaden.com	t	f	\N	outlook.com	Tucows Domains Inc.	2028-10-22	{hostdns1.doruk.net.tr,hostdns2.doruk.net.tr,hostdns3.doruk.net.tr}	success	2025-11-15 21:08:51.066602+00	\N	\N
16	batmaztekstil.com.tr	t	f	\N	outlook.com	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
18	dardagangida.com.tr	t	f	\N	dardagangida.com.tr	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
19	dinkgida.com.tr	t	f	\N	dinkgida.com.tr	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
20	dirakman.com	t	t	\N	dirakman.com	PDR Ltd. d/b/a PublicDomainRegistry.com	2026-12-19	{ns1.guzelhosting.com,ns11.guzelhosting.com,ns12.guzelhosting.com,ns2.guzelhosting.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
22	eralpkazan.com	t	f	none	vit.com.tr	IHS Telekom, Inc.	2026-01-17	{ns1.ulutek.net,ns2.ulutek.net}	success	2025-11-15 21:08:51.066602+00	\N	\N
23	eralpkazan.com	t	f	none	vit.com.tr	IHS Telekom, Inc.	2026-01-17	{ns1.ulutek.net,ns2.ulutek.net}	success	2025-11-15 21:08:51.066602+00	\N	\N
24	ertugmetal.com	t	f	\N	outlook.com	Nics Telekomunikasyon A.S.	2028-07-04	{ns1.natrohost.com,ns2.natrohost.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
25	ertugrulhelva.com	t	f	\N	natrohost.com	Nics Telekomunikasyon A.S.	2027-02-05	{ns1.natrohost.com,ns2.natrohost.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
26	eruslusaglik.com.tr	t	t	none	trendmicro.eu	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
27	fimaks.com	t	t	none	outlook.com	Nics Telekomunikasyon A.S.	2025-12-12	{ns1.natrohost.com,ns2.natrohost.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
29	gurtanplastik.com	t	f	\N	google.com	Nics Telekomunikasyon A.S.	2026-06-13	{ns5.dnssaglayici.com,ns6.dnssaglayici.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
30	mkpguvenal.com	t	f	\N	mkpguvenal.com	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2025-12-11	{bursa.profornet.net,merkez.profornet.net}	success	2025-11-15 21:08:51.066602+00	\N	\N
31	harputtekstil.com.tr	t	f	quarantine	harputholding.com.tr	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
32	igrek.com.tr	t	t	none	bulutino.com	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
33	igrek.com.tr	t	t	none	bulutino.com	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
34	indotekstil.com	t	t	none	kriweb.com	Atak Domain Bilgi Teknolojileri A.S.	2028-05-10	{ns1.kriweb.com,ns2.kriweb.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
35	toruntex.com	t	f	\N	google.com	Cronon GmbH	2026-03-31	{ns12.wixdns.net,ns13.wixdns.net}	success	2025-11-15 21:08:51.066602+00	\N	\N
36	kametsanmetal.com.tr	f	f	\N	\N	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
37	yuzgullu.com	f	f	\N	\N	GoDaddy.com, LLC	2026-04-07	{arely.ns.cloudflare.com,cosmin.ns.cloudflare.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
38	kirayteks.com.tr	t	f	quarantine	trendmicro.eu	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
39	kocayusufmakine.com	t	t	none	mxrouting.net	PDR Ltd. d/b/a PublicDomainRegistry.com	2029-03-28	{ns1.crewmedya.tr,ns2.crewmedya.tr}	success	2025-11-15 21:08:51.066602+00	\N	\N
40	celikdovme.com	t	f	\N	yandex.net	FBS Inc.	2026-03-08	{eu.dnsenable.com,tr.dnsenable.com,us.dnsenable.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
42	midoser.com	t	t	\N	midoser.com	Cizgi Telekomunikasyon A.S.	2030-04-06	{austin.ns.cloudflare.com,dayana.ns.cloudflare.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
43	miraheating.com	t	f	\N	miraheating.com	PDR Ltd. d/b/a PublicDomainRegistry.com	2026-10-17	{ns1.wee22.com,ns2.wee22.com,ns3.wee22.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
44	otega.com.tr	t	f	\N	otega.com.tr	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
45	rollmech.com	t	f	\N	ppe-hosted.com	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2026-05-06	{dnx1.vodafone.net.tr,dnx2.vodafone.net.tr}	success	2025-11-15 21:08:51.066602+00	\N	\N
46	sezermac.com	t	f	none	yandex.net	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2033-12-17	{vds5.armdns.com,vds6.armdns.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
47	simetrikpro.com	t	f	none	outlook.com	FBS Inc.	2026-06-10	{ns1.artiiki.com,ns2.artiiki.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
48	tarimsalkimya.com.tr	t	t	quarantine	barracudanetworks.com	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
49	tarimsalkimya.com.tr	t	t	quarantine	barracudanetworks.com	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
50	ucge-drs.com	f	f	\N	\N	Amazon Registrar, Inc.	2026-03-16	{ns1.tekkilavuz.com,ns2.tekkilavuz.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
51	unalsan.com	t	f	reject	unalsan.com	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2028-11-09	{dina.ns.cloudflare.com,rick.ns.cloudflare.com}	success	2025-11-15 21:08:51.066602+00	\N	\N
52	yurektekstil.com.tr	t	f	none	yurektekstil.com.tr	\N	\N	\N	whois_failed	2025-11-15 21:08:51.066602+00	\N	\N
53	asteknikvana.com	t	t	reject	outlook.com	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2026-01-17	{ns1.entetanitim.com,ns2.entetanitim.com}	completed	2025-11-15 21:10:52.136131+00	\N	100
54	dmkimya.com.tr	t	t	\N	GOOGLE.COM	\N	\N	\N	completed	2025-11-15 21:11:25.334024+00	\N	100
55	globteks.com	t	t	reject	yandex.net	IHS Telekom, Inc.	2027-02-26	{ns1.ihsdnsx29.com,ns2.ihsdnsx29.com}	completed	2025-11-15 21:11:48.969132+00	\N	100
56	matli.com.tr	t	f	reject	outlook.com	\N	\N	\N	completed	2025-11-15 21:12:31.165856+00	\N	100
57	bircanplastik.com	t	t	\N	yandex.net	ODTU Gelistirme Vakfi Bilgi Teknolojileri Sanayi Ve Ticaret Anonim Sirketi	2026-01-21	{ns1.kggsoft.net,ns2.kggsoft.net}	completed	2025-11-15 21:13:13.676648+00	\N	100
58	argos.com.tr	t	f	\N	GOOGLE.COM	\N	\N	\N	completed	2025-11-15 21:13:30.010535+00	\N	100
60	atilimyem.com.tr	t	t	quarantine	atilimyem.com.tr	\N	\N	\N	completed	2025-11-15 21:14:20.316134+00	\N	100
\.


--
-- Data for Name: lead_scores; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.lead_scores (id, domain, readiness_score, segment, reason, updated_at) FROM stdin;
1	example.com	40	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 40, Provider: Unknown	2025-11-15 20:49:43.354589+00
2	test.com	0	Skip	Hard-fail: MX kaydı yok	2025-11-15 20:54:17.150663+00
5	gibibyte.com.tr	60	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 60, Provider: M365	2025-11-15 21:05:50.192447+00
6	meptur.com.tr	45	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 45, Provider: M365	2025-11-15 21:06:22.016821+00
7	aydinboya.com	20	Skip	Yetersiz veri, analiz dışı. Score: 20, Provider: Local	2025-11-15 21:08:51.066602+00
8	acaraku.com.tr	5	Skip	Yetersiz veri, analiz dışı. Score: 5, Provider: Local	2025-11-15 21:08:51.066602+00
9	alfateks.com.tr	0	Skip	Yetersiz veri, analiz dışı. Score: 0, Provider: Local	2025-11-15 21:08:51.066602+00
10	gumus.com.tr	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Google	2025-11-15 21:08:51.066602+00
11	gumus.com.tr	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Google	2025-11-15 21:08:51.066602+00
15	baritmaden.com	45	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 45, Provider: M365	2025-11-15 21:08:51.066602+00
16	batmaztekstil.com.tr	45	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 45, Provider: M365	2025-11-15 21:08:51.066602+00
18	dardagangida.com.tr	5	Skip	Yetersiz veri, analiz dışı. Score: 5, Provider: Local	2025-11-15 21:08:51.066602+00
19	dinkgida.com.tr	5	Skip	Yetersiz veri, analiz dışı. Score: 5, Provider: Local	2025-11-15 21:08:51.066602+00
20	dirakman.com	30	Skip	Yetersiz veri, analiz dışı. Score: 30, Provider: Local	2025-11-15 21:08:51.066602+00
22	eralpkazan.com	0	Skip	Yetersiz veri, analiz dışı. Score: 0, Provider: Local	2025-11-15 21:08:51.066602+00
23	eralpkazan.com	0	Skip	Yetersiz veri, analiz dışı. Score: 0, Provider: Local	2025-11-15 21:08:51.066602+00
24	ertugmetal.com	45	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 45, Provider: M365	2025-11-15 21:08:51.066602+00
25	ertugrulhelva.com	5	Skip	Yetersiz veri, analiz dışı. Score: 5, Provider: Local	2025-11-15 21:08:51.066602+00
26	eruslusaglik.com.tr	20	Skip	Yetersiz veri, analiz dışı. Score: 20, Provider: Local	2025-11-15 21:08:51.066602+00
27	fimaks.com	60	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 60, Provider: M365	2025-11-15 21:08:51.066602+00
29	gurtanplastik.com	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Google	2025-11-15 21:08:51.066602+00
30	mkpguvenal.com	5	Skip	Yetersiz veri, analiz dışı. Score: 5, Provider: Local	2025-11-15 21:08:51.066602+00
31	harputtekstil.com.tr	20	Skip	Yetersiz veri, analiz dışı. Score: 20, Provider: Local	2025-11-15 21:08:51.066602+00
32	igrek.com.tr	20	Skip	Yetersiz veri, analiz dışı. Score: 20, Provider: Local	2025-11-15 21:08:51.066602+00
33	igrek.com.tr	20	Skip	Yetersiz veri, analiz dışı. Score: 20, Provider: Local	2025-11-15 21:08:51.066602+00
34	indotekstil.com	20	Skip	Yetersiz veri, analiz dışı. Score: 20, Provider: Local	2025-11-15 21:08:51.066602+00
35	toruntex.com	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Google	2025-11-15 21:08:51.066602+00
36	kametsanmetal.com.tr	0	Skip	Hard-fail: MX kaydı yok	2025-11-15 21:08:51.066602+00
37	yuzgullu.com	0	Skip	Hard-fail: MX kaydı yok	2025-11-15 21:08:51.066602+00
38	kirayteks.com.tr	20	Skip	Yetersiz veri, analiz dışı. Score: 20, Provider: Local	2025-11-15 21:08:51.066602+00
39	kocayusufmakine.com	20	Skip	Yetersiz veri, analiz dışı. Score: 20, Provider: Local	2025-11-15 21:08:51.066602+00
40	celikdovme.com	25	Skip	Yetersiz veri, analiz dışı. Score: 25, Provider: Yandex	2025-11-15 21:08:51.066602+00
42	midoser.com	30	Skip	Yetersiz veri, analiz dışı. Score: 30, Provider: Local	2025-11-15 21:08:51.066602+00
43	miraheating.com	5	Skip	Yetersiz veri, analiz dışı. Score: 5, Provider: Local	2025-11-15 21:08:51.066602+00
44	otega.com.tr	5	Skip	Yetersiz veri, analiz dışı. Score: 5, Provider: Local	2025-11-15 21:08:51.066602+00
45	rollmech.com	5	Skip	Yetersiz veri, analiz dışı. Score: 5, Provider: Local	2025-11-15 21:08:51.066602+00
46	sezermac.com	15	Skip	Yetersiz veri, analiz dışı. Score: 15, Provider: Yandex	2025-11-15 21:08:51.066602+00
47	simetrikpro.com	35	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 35, Provider: M365	2025-11-15 21:08:51.066602+00
48	tarimsalkimya.com.tr	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Local	2025-11-15 21:08:51.066602+00
49	tarimsalkimya.com.tr	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Local	2025-11-15 21:08:51.066602+00
50	ucge-drs.com	0	Skip	Hard-fail: MX kaydı yok	2025-11-15 21:08:51.066602+00
51	unalsan.com	25	Skip	Yetersiz veri, analiz dışı. Score: 25, Provider: Local	2025-11-15 21:08:51.066602+00
52	yurektekstil.com.tr	0	Skip	Yetersiz veri, analiz dışı. Score: 0, Provider: Local	2025-11-15 21:08:51.066602+00
53	asteknikvana.com	90	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 90, Provider: M365	2025-11-15 21:10:52.136131+00
54	dmkimya.com.tr	70	Migration	Cloud kullanıcıları, geçişe hazır. Score: 70, Provider: Google	2025-11-15 21:11:25.334024+00
55	globteks.com	70	Migration	Cloud kullanıcıları, geçişe hazır. Score: 70, Provider: Yandex	2025-11-15 21:11:48.969132+00
56	matli.com.tr	65	Existing	Zaten M365 kullanıyor, koruma/upsell potansiyeli. Score: 65, Provider: M365	2025-11-15 21:12:31.165856+00
57	bircanplastik.com	50	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 50, Provider: Yandex	2025-11-15 21:13:13.676648+00
58	argos.com.tr	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Google	2025-11-15 21:13:30.010535+00
60	atilimyem.com.tr	45	Cold	Zayıf sinyaller, daha fazla veri gerek. Score: 45, Provider: Local	2025-11-15 21:14:20.316134+00
\.


--
-- Data for Name: raw_leads; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.raw_leads (id, source, company_name, email, website, domain, payload, ingested_at) FROM stdin;
1	domain	\N	\N	\N	example.com	{"email": null, "website": null, "original_domain": "example.com"}	2025-11-15 20:49:43.323765+00
2	domain	Test Inc	\N	\N	test.com	{"email": null, "website": null, "original_domain": "test.com"}	2025-11-15 20:54:17.387892+00
3	domain	\N	\N	\N	meptur.com.tr	{"email": null, "website": null, "original_domain": "meptur.com.tr"}	2025-11-15 20:56:45.016475+00
4	domain	gibibyte	\N	\N	gibibyte.com.tr	{"email": null, "website": null, "original_domain": "gibibyte.com.tr"}	2025-11-15 21:01:53.262786+00
5	domain	gibibyte	\N	\N	gibibyte.com.tr	{"email": null, "website": null, "original_domain": "gibibyte.com.tr"}	2025-11-15 21:05:50.142367+00
6	domain	meptur	\N	\N	meptur.com.tr	{"email": null, "website": null, "original_domain": "meptur.com.tr"}	2025-11-15 21:06:21.990418+00
7	csv	ABS GRUP BOYA VE KİMYA SAN.TİC.LTD.ŞTİ.	\N	\N	aydinboya.com	{"email": null, "website": null, "row_index": 4, "original_domain": "https://www.aydinboya.com"}	2025-11-15 21:08:49.881115+00
8	csv	ACAR AKÜ MALZ.İÇ VE DIŞ TİC.LTD.ŞTİ.	\N	\N	acaraku.com.tr	{"email": null, "website": null, "row_index": 5, "original_domain": "http://www.acaraku.com.tr/"}	2025-11-15 21:08:49.891185+00
9	csv	ALFATEKS TEKSTİL ÜRÜNLERİ MADENCİLİK SAN.VE TİC.A.Ş.	\N	\N	alfateks.com.tr	{"email": null, "website": null, "row_index": 7, "original_domain": "http://www.alfateks.com.tr/"}	2025-11-15 21:08:49.898878+00
10	csv	AQUA ANA MEŞRUBAT A.Ş.	\N	\N	gumus.com.tr	{"email": null, "website": null, "row_index": 8, "original_domain": "https://www.gumus.com.tr/"}	2025-11-15 21:08:49.905785+00
11	csv	AQUA ANA MEŞRUBAT A.Ş.	\N	\N	gumus.com.tr	{"email": null, "website": null, "row_index": 9, "original_domain": "https://www.gumus.com.tr/"}	2025-11-15 21:08:49.911993+00
12	csv	ARGOS DIŞ TİCARET LTD.ŞTİ.	\N	\N	argos.com.tr	{"email": null, "website": null, "row_index": 10, "original_domain": "http://www.argos.com.tr/"}	2025-11-15 21:08:49.920961+00
13	csv	ASTEKNİK MAK.SAN.VE TİC.A.Ş.	\N	\N	asteknikvana.com	{"email": null, "website": null, "row_index": 11, "original_domain": "http://www.asteknikvana.com/"}	2025-11-15 21:08:49.93015+00
14	csv	ATILIM YEM TARIM NAK.HAYVANCILIK VE ÜRÜN.GIDA SAN.TİC.LTD.ŞTİ.	\N	\N	atilimyem.com.tr	{"email": null, "website": null, "row_index": 12, "original_domain": "http://atilimyem.com.tr/"}	2025-11-15 21:08:49.93797+00
15	csv	BARİT MADEN TÜRK A.Ş.	\N	\N	baritmaden.com	{"email": null, "website": null, "row_index": 13, "original_domain": "http://www.baritmaden.com/"}	2025-11-15 21:08:49.945089+00
16	csv	BATMAZ TEKSTİL SANAYİ VE  TİCARET LTD.ŞTİ.	\N	\N	batmaztekstil.com.tr	{"email": null, "website": null, "row_index": 14, "original_domain": "http://www.batmaztekstil.com.tr/"}	2025-11-15 21:08:49.952937+00
17	csv	BİRCAN KİMYA PLASTİK SAN.VE TİC.A.Ş.	\N	\N	bircanplastik.com	{"email": null, "website": null, "row_index": 15, "original_domain": "http://www.bircanplastik.com/"}	2025-11-15 21:08:49.960397+00
18	csv	DARDAĞAN GIDA SAN.VE TİC.LTD.ŞTİ.	\N	\N	dardagangida.com.tr	{"email": null, "website": null, "row_index": 17, "original_domain": "http://www.dardagangida.com.tr/"}	2025-11-15 21:08:49.968017+00
19	csv	DİNK GIDA SAN.VE TİC.LTD.ŞTİ.	\N	\N	dinkgida.com.tr	{"email": null, "website": null, "row_index": 19, "original_domain": "http://www.dinkgida.com.tr/"}	2025-11-15 21:08:49.974712+00
20	csv	DIRAKMAN SÜTLÜ VE UNLU MAMÜLLER SAN.VE TİC.LTD.ŞTİ.	\N	\N	dirakman.com	{"email": null, "website": null, "row_index": 20, "original_domain": "http://www.dirakman.com/"}	2025-11-15 21:08:49.98233+00
21	csv	DM YAPI VE MADEN KİMYASALLARI KİMYEVİ  ÜRÜNLER İTHALAT İHR.TİC.VE SAN.LTD.ŞTİ.	\N	\N	dmkimya.com.tr	{"email": null, "website": null, "row_index": 21, "original_domain": "http://www.dmkimya.com.tr/"}	2025-11-15 21:08:49.988937+00
22	csv	ERALP MAKİNE KAZAN KİMYA VE EKİPMANLARI  SAN.VE TİC.LTD.ŞTİ.	\N	\N	eralpkazan.com	{"email": null, "website": null, "row_index": 22, "original_domain": "http://www.eralpkazan.com/"}	2025-11-15 21:08:49.995831+00
23	csv	ERALP MAKİNE KAZAN KİMYA VE EKİPMANLARI  SAN.VE TİC.LTD.ŞTİ.	\N	\N	eralpkazan.com	{"email": null, "website": null, "row_index": 23, "original_domain": "http://www.eralpkazan.com/"}	2025-11-15 21:08:50.002563+00
24	csv	ERTUĞ METAL DÖKÜM MAKİNA SAN.VE TİC. A.Ş.	\N	\N	ertugmetal.com	{"email": null, "website": null, "row_index": 24, "original_domain": "http://www.ertugmetal.com/"}	2025-11-15 21:08:50.009615+00
25	csv	ERTUĞRUL HELVA TAHİN SUSAM GIDA İTHALAT İHRACAT SAN.VE TİC. LTD.ŞTİ.	\N	\N	ertugrulhelva.com	{"email": null, "website": null, "row_index": 25, "original_domain": "http://www.ertugrulhelva.com/"}	2025-11-15 21:08:50.016302+00
26	csv	ERUSLU  SAĞLIK ÜRÜNLERİ SAN.VE TİC.A.Ş.	\N	\N	eruslusaglik.com.tr	{"email": null, "website": null, "row_index": 26, "original_domain": "https://eruslusaglik.com.tr/"}	2025-11-15 21:08:50.023085+00
27	csv	FİMAKS MAKİNA GIDA VE TARIM ÜRÜNLERİ SAN.TİC.A.Ş.	\N	\N	fimaks.com	{"email": null, "website": null, "row_index": 27, "original_domain": "http://www.fimaks.com/"}	2025-11-15 21:08:50.032014+00
28	csv	GLOBTEKS İPLİK SAN.TİC.LTD.ŞTİ.	\N	\N	globteks.com	{"email": null, "website": null, "row_index": 28, "original_domain": "http://www.globteks.com/"}	2025-11-15 21:08:50.04033+00
29	csv	GÜRTAN PLASTİK SAN.VE TİC.LTD.ŞTİ.	\N	\N	gurtanplastik.com	{"email": null, "website": null, "row_index": 30, "original_domain": "http://www.gurtanplastik.com/"}	2025-11-15 21:08:50.047863+00
30	csv	GÜVENAL TATLI SANAYİ VE TİCARET LİMİTED ŞİRKETİ	\N	\N	mkpguvenal.com	{"email": null, "website": null, "row_index": 31, "original_domain": "http://www.mkpguvenal.com"}	2025-11-15 21:08:50.054726+00
31	csv	HARPUT TEKSTİL SANAYİ VE TİCARET A.Ş.-MİRANLI ŞUBE	\N	\N	harputtekstil.com.tr	{"email": null, "website": null, "row_index": 32, "original_domain": "http://www.harputtekstil.com.tr/"}	2025-11-15 21:08:50.062763+00
32	csv	İĞREK MAKİNE SAN.VE TİC.A.Ş.	\N	\N	igrek.com.tr	{"email": null, "website": null, "row_index": 33, "original_domain": "http://www.igrek.com.tr/"}	2025-11-15 21:08:50.070535+00
33	csv	İĞREK MAKİNE SAN.VE TİC.A.Ş.	\N	\N	igrek.com.tr	{"email": null, "website": null, "row_index": 34, "original_domain": "http://www.igrek.com.tr/"}	2025-11-15 21:08:50.077916+00
34	csv	İNDO TEKSTİL VE DOKUMA SAN.TİC.A.Ş.	\N	\N	indotekstil.com	{"email": null, "website": null, "row_index": 35, "original_domain": "http://www.indotekstil.com/"}	2025-11-15 21:08:50.084855+00
35	csv	İNTRO TARIM VE HAYVANCILIK A.Ş.	\N	\N	toruntex.com	{"email": null, "website": null, "row_index": 36, "original_domain": "https://www.toruntex.com/"}	2025-11-15 21:08:50.092643+00
36	csv	KAMETSAN METAL İNŞAAT SAN.VE TİC.A.Ş.	\N	\N	kametsanmetal.com.tr	{"email": null, "website": null, "row_index": 37, "original_domain": "www.kametsanmetal.com.tr"}	2025-11-15 21:08:50.100066+00
37	csv	KAZIM YÜZGÜLLÜ	\N	\N	yuzgullu.com	{"email": null, "website": null, "row_index": 38, "original_domain": "http://yuzgullu.com/"}	2025-11-15 21:08:50.112707+00
38	csv	KIRAYTEKS TEKSTİL SAN.VE TİC.LTD.ŞTİ.	\N	\N	kirayteks.com.tr	{"email": null, "website": null, "row_index": 39, "original_domain": "http://kirayteks.com.tr/"}	2025-11-15 21:08:50.120245+00
39	csv	KOCAYUSUF AĞAÇ MAKİNALARI SANAYİ VE TİCARET LTD.ŞTİ.	\N	\N	kocayusufmakine.com	{"email": null, "website": null, "row_index": 40, "original_domain": "http://www.kocayusufmakine.com"}	2025-11-15 21:08:50.128772+00
40	csv	KSM METAL DÖVME MADENCİLİK İNŞ.SAN.TİC.LTD.ŞTİ.	\N	\N	celikdovme.com	{"email": null, "website": null, "row_index": 41, "original_domain": "http://www.celikdovme.com/"}	2025-11-15 21:08:50.136009+00
41	csv	MATLI YEM SANAYİİ VE TİCARET A.Ş.	\N	\N	matli.com.tr	{"email": null, "website": null, "row_index": 43, "original_domain": "http://www.matli.com.tr/"}	2025-11-15 21:08:50.152103+00
42	csv	MİDOSER MODÜLER MOBİLYA İTH.İHR.SAN.VE TİC.LTD.ŞTİ.	\N	\N	midoser.com	{"email": null, "website": null, "row_index": 45, "original_domain": "https://midoser.com/"}	2025-11-15 21:08:50.160426+00
43	csv	MİRA ISI SİSTEMLERİ MÜHENDİSLİK SAN. ve TİC. LTD. ŞTİ.	\N	\N	miraheating.com	{"email": null, "website": null, "row_index": 46, "original_domain": "http://www.miraheating.com/"}	2025-11-15 21:08:50.167416+00
44	csv	OTEGA TARIM HAYVANCILIK GIDA LOJİSTİK MAKİNE SAN.VE TİC.LTD.ŞTİ.	\N	\N	otega.com.tr	{"email": null, "website": null, "row_index": 49, "original_domain": "http://www.otega.com.tr/"}	2025-11-15 21:08:50.174064+00
45	csv	ROLLPANEL YALITIM VE İNŞAAT MALZ.SAN.TİC.A.Ş.	\N	\N	rollmech.com	{"email": null, "website": null, "row_index": 52, "original_domain": "http://www.rollmech.com/"}	2025-11-15 21:08:50.181181+00
46	csv	SEZER TARIM VE SAĞIM TEKN.SAN.TİC.LTD.ŞTİ. M.K.PAŞA ŞUBESİ	\N	\N	sezermac.com	{"email": null, "website": null, "row_index": 53, "original_domain": "http://www.sezermac.com/"}	2025-11-15 21:08:50.190027+00
47	csv	SİMETRİK PRO ÜRETİM SİSTEM ÇÖZ.VE END.EKİPM.TEK.SAN.VE TİC.LTD.ŞTİ.	\N	\N	simetrikpro.com	{"email": null, "website": null, "row_index": 54, "original_domain": "https://www.simetrikpro.com/"}	2025-11-15 21:08:50.197135+00
48	csv	TARIMSAL KİMYA TEK.SAN.VE TİC.A.Ş.	\N	\N	tarimsalkimya.com.tr	{"email": null, "website": null, "row_index": 56, "original_domain": "http://www.tarimsalkimya.com.tr/"}	2025-11-15 21:08:50.204161+00
49	csv	TARIMSAL KİMYA TEK.SAN.VE TİC.A.Ş.	\N	\N	tarimsalkimya.com.tr	{"email": null, "website": null, "row_index": 57, "original_domain": "http://www.tarimsalkimya.com.tr/"}	2025-11-15 21:08:50.211375+00
50	csv	ÜÇGE DRS DEPO RAF SİSTEMLERİ PAZARLAMA SAN.VE TİC.A.Ş.	\N	\N	ucge-drs.com	{"email": null, "website": null, "row_index": 58, "original_domain": "http://www.ucge-drs.com"}	2025-11-15 21:08:50.226721+00
51	csv	ÜNALSAN METAL VE MAKİNA SAN.VE TİC.A.Ş.	\N	\N	unalsan.com	{"email": null, "website": null, "row_index": 59, "original_domain": "https://unalsan.com/"}	2025-11-15 21:08:50.233946+00
52	csv	YÜREK TEKSTİL SANAYİ VE TİCARET A.Ş.	\N	\N	yurektekstil.com.tr	{"email": null, "website": null, "row_index": 61, "original_domain": "http://www.yurektekstil.com.tr/"}	2025-11-15 21:08:50.240863+00
\.


--
-- Data for Name: webhook_retries; Type: TABLE DATA; Schema: public; Owner: dyn365hunter
--

COPY public.webhook_retries (id, api_key_id, payload, domain, retry_count, max_retries, next_retry_at, status, error_message, created_at, last_retry_at) FROM stdin;
\.


--
-- Name: api_keys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.api_keys_id_seq', 1, false);


--
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.companies_id_seq', 46, true);


--
-- Name: domain_signals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.domain_signals_id_seq', 60, true);


--
-- Name: lead_scores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.lead_scores_id_seq', 60, true);


--
-- Name: raw_leads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.raw_leads_id_seq', 52, true);


--
-- Name: webhook_retries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dyn365hunter
--

SELECT pg_catalog.setval('public.webhook_retries_id_seq', 1, false);


--
-- Name: api_keys api_keys_key_hash_key; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_key_hash_key UNIQUE (key_hash);


--
-- Name: api_keys api_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_pkey PRIMARY KEY (id);


--
-- Name: companies companies_domain_key; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_domain_key UNIQUE (domain);


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
-- Name: lead_scores lead_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.lead_scores
    ADD CONSTRAINT lead_scores_pkey PRIMARY KEY (id);


--
-- Name: raw_leads raw_leads_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.raw_leads
    ADD CONSTRAINT raw_leads_pkey PRIMARY KEY (id);


--
-- Name: webhook_retries webhook_retries_pkey; Type: CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.webhook_retries
    ADD CONSTRAINT webhook_retries_pkey PRIMARY KEY (id);


--
-- Name: idx_api_keys_is_active; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_api_keys_is_active ON public.api_keys USING btree (is_active);


--
-- Name: idx_api_keys_key_hash; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_api_keys_key_hash ON public.api_keys USING btree (key_hash);


--
-- Name: idx_api_keys_last_used_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_api_keys_last_used_at ON public.api_keys USING btree (last_used_at);


--
-- Name: idx_companies_contact_quality_score; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_companies_contact_quality_score ON public.companies USING btree (contact_quality_score);


--
-- Name: idx_companies_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_companies_domain ON public.companies USING btree (domain);


--
-- Name: idx_companies_provider; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_companies_provider ON public.companies USING btree (provider);


--
-- Name: idx_companies_tenant_size; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_companies_tenant_size ON public.companies USING btree (tenant_size);


--
-- Name: idx_companies_updated_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_companies_updated_at ON public.companies USING btree (updated_at);


--
-- Name: idx_domain_signals_dmarc_coverage; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_domain_signals_dmarc_coverage ON public.domain_signals USING btree (dmarc_coverage);


--
-- Name: idx_domain_signals_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_domain_signals_domain ON public.domain_signals USING btree (domain);


--
-- Name: idx_domain_signals_local_provider; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_domain_signals_local_provider ON public.domain_signals USING btree (local_provider);


--
-- Name: idx_domain_signals_mx_root; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_domain_signals_mx_root ON public.domain_signals USING btree (mx_root);


--
-- Name: idx_domain_signals_scan_status; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_domain_signals_scan_status ON public.domain_signals USING btree (scan_status);


--
-- Name: idx_domain_signals_scanned_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_domain_signals_scanned_at ON public.domain_signals USING btree (scanned_at);


--
-- Name: idx_lead_scores_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_lead_scores_domain ON public.lead_scores USING btree (domain);


--
-- Name: idx_lead_scores_readiness_score; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_lead_scores_readiness_score ON public.lead_scores USING btree (readiness_score);


--
-- Name: idx_lead_scores_segment; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_lead_scores_segment ON public.lead_scores USING btree (segment);


--
-- Name: idx_lead_scores_updated_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_lead_scores_updated_at ON public.lead_scores USING btree (updated_at);


--
-- Name: idx_raw_leads_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_raw_leads_domain ON public.raw_leads USING btree (domain);


--
-- Name: idx_raw_leads_ingested_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_raw_leads_ingested_at ON public.raw_leads USING btree (ingested_at);


--
-- Name: idx_raw_leads_source; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_raw_leads_source ON public.raw_leads USING btree (source);


--
-- Name: idx_webhook_retries_api_key_id; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_webhook_retries_api_key_id ON public.webhook_retries USING btree (api_key_id);


--
-- Name: idx_webhook_retries_domain; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_webhook_retries_domain ON public.webhook_retries USING btree (domain);


--
-- Name: idx_webhook_retries_next_retry_at; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_webhook_retries_next_retry_at ON public.webhook_retries USING btree (next_retry_at);


--
-- Name: idx_webhook_retries_status; Type: INDEX; Schema: public; Owner: dyn365hunter
--

CREATE INDEX idx_webhook_retries_status ON public.webhook_retries USING btree (status);


--
-- Name: domain_signals domain_signals_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.domain_signals
    ADD CONSTRAINT domain_signals_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: lead_scores lead_scores_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.lead_scores
    ADD CONSTRAINT lead_scores_domain_fkey FOREIGN KEY (domain) REFERENCES public.companies(domain) ON DELETE CASCADE;


--
-- Name: webhook_retries webhook_retries_api_key_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyn365hunter
--

ALTER TABLE ONLY public.webhook_retries
    ADD CONSTRAINT webhook_retries_api_key_id_fkey FOREIGN KEY (api_key_id) REFERENCES public.api_keys(id) ON DELETE SET NULL;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: dyn365hunter
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict E0qu0MYNbUrhaXQaLlE18E1hg0dFf6m2oqoWB7gSorlGLbDwUEyZMjhDXfm06SB

