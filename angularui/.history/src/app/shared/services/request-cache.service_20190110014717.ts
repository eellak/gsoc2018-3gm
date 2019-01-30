import { Injectable } from '@angular/core';
import { HttpRequest, HttpResponse } from '@angular/common/http';
import { LocalStorage } from '@ngx-pwa/local-storage';
import { mergeMap, filter, switchMap, map } from 'rxjs/operators';
import { from } from 'rxjs';

export interface RequestCacheEntry {
  url: string;
  response: HttpResponse<any>;
  lastRead: number;
}

// #docregion request-cache
export abstract class RequestCache {
  abstract get(req: HttpRequest<any>): HttpResponse<any> | undefined;
  abstract put(req: HttpRequest<any>, response: HttpResponse<any>): void;
}
// #enddocregion request-cache

const maxAge = 300000; // maximum cache age (ms)  5min

@Injectable()
export class RequestCacheWithMap implements RequestCache {

  cache = new Map<string, RequestCacheEntry>();

  constructor() { }

  get(req: HttpRequest<any>): HttpResponse<any> | undefined {
    const url = req.urlWithParams;
    const cached = this.cache.get(url);

    if (!cached) {
      return undefined;
    }

    const isExpired = cached.lastRead < (Date.now() - maxAge);
    const expired = isExpired ? 'expired ' : '';
    console.log(`Found ${expired}cached response for "${url}".`);
    return isExpired ? undefined : cached.response;
  }

  put(req: HttpRequest<any>, response: HttpResponse<any>): void {
    const url = req.urlWithParams;
    console.log(`Caching response from "${url}".`);

    if (response.body) {
      console.log('response cached [ok]');
      const entry = { url, response, lastRead: Date.now() };
      this.cache.set(url, entry);
    }
    // remove expired cache entries
    const expired = Date.now() - maxAge;
    this.cache.forEach(entry => {
      if (entry.lastRead < expired) {
        this.cache.delete(entry.url);
      }
    });

    console.log(`Request cache size: ${this.cache.size}.`);
  }
}


/*
LocalStorage Implementation

*/
@Injectable()
export class RequestCacheWithLocalStorage implements RequestCache {


  constructor(protected cache: LocalStorage) {}

  get(req: HttpRequest<any>): HttpResponse<any> | undefined {
    const url = req.urlWithParams;
    let cached = null;
    this.cache.getUnsafeItem<RequestCacheEntry>(url).subscribe((data) => {
      cached = data;
    });

    if (!cached || cached == null) {
      return undefined;
    }

    const isExpired = cached.lastRead < (Date.now() - maxAge);
    const expired = isExpired ? 'expired ' : '';
    console.log(`Found ${expired}cached response for "${url}".`);
    return isExpired ? undefined : cached.response;
  }

  put(req: HttpRequest<any>, response: HttpResponse<any>): void {
    const url = req.urlWithParams;
    console.log(`Caching response from "${url}".`);

    if (response.body) {
      const entry = { url, response, lastRead: Date.now() };
      this.cache.setItem(url, entry).subscribe(() => {
        console.log('response cached [ok]');
      });
    }
    // remove expired cache entries
    const expired = Date.now() - maxAge;
    this.cache.keys().pipe(
      mergeMap((keys) => from(keys)),
      switchMap((key) =>  this.cache.getUnsafeItem<RequestCacheEntry>(key)),
      filter((item) => item.lastRead < expired), /* Keep only keys starting with 'app_' */
      mergeMap((item) => this.cache.removeItem(item.url))       /* Remove the item for each key */
    ).subscribe({ complete: () => {
       // we want to act only when all the operations are done */
      console.log('Done!');
    } });

    console.log(`Request cache size: ${this.cache.size}.`);
  }
}
