export interface LegalIndexItem {
    _id: string;
    name: number;
    type: string;
    year: number;
    rank?: number;
}

export interface Topic {
    _id: number;
    keywords: string[];
    statutes: string[];
}

export interface Statute extends  LegalIndexItem {
    titleGR?: string;
    archive?: string;
}

export interface IArchiveStatsResource {
    count_all: number;
    count_last30days: number;
    count_last7days: number;
    count_today: number;
}

export interface StatuteStatsResource {
    res_laws_total: number;
    res_links_total: number;
    res_topics_total: number;
    last_5_laws?: LegalIndexItem[];
    last_5_pd?: LegalIndexItem[];
    top_5_laws?: LegalIndexItem[];
    iarchive_stats?: IArchiveStatsResource;
}



export interface Article {
    [key: string]: Paragraph  ;
    }


export interface Paragraph {
    [key: string]: string[]  ;
}

export interface StatuteHistoryItem {
    identifier: string;
    amendee: string;
    amendee_date?: string;
    issue?: string;
    summary?: string;
    archive?: string;
}

export interface StatuteLinks {
    incoming: StatuteLinkItem;
    outgoing: StatuteLinkItem;
}

export interface StatuteLinkItem {
    [key: string]: string[][];
}
