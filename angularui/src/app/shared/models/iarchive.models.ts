export interface IaResource {
    identifier: string;
    title: string;
    addeddate: Date;
    name?: string;
    date?: Date;
    year?: number;
    month?: number;
    downloads?: string;
    item_size?: string;
}

export interface IaStatsResource {
    res_count_total: number;
    res_count_lastyear: number;
    res_count_lastmonth: number;
    res_count_lastweek: number;
    res_last_docs?: IaResource[];
}


