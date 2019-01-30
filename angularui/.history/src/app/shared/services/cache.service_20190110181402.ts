import { Injectable } from '@angular/core';
import { HttpRequest, HttpResponse } from '@angular/common/http';

import { LocalStorage } from '@ngx-pwa/local-storage';
import { mergeMap, filter, switchMap, map } from 'rxjs/operators';
import { from, Observable, of } from 'rxjs';
import { isNil } from '../helpers/utils';

export interface RequestCacheEntry {
  url: string;
  response: HttpResponse<any>;
  lastRead: number;
}

export abstract class RequestCache {
  abstract get(req: HttpRequest<any>):  Observable<HttpResponse<any>> | undefined;
  abstract put(req: HttpRequest<any>, response: HttpResponse<any>): void;
}

const maxAgeInMemory = 300000; // maximum InMemory cache age (ms)  5min
const maxAgeInLocalStorage = 300000 * 2; // maximum InMemory cache age (ms)   10min

/*
  LocalStorage Implementation
*/

@Injectable()
export class RequestCacheWithLocalStorage implements RequestCache {

  memorycache = new Map<string, RequestCacheEntry>();

  constructor(
    protected storagecache: LocalStorage,
) {}

  get(req: HttpRequest<any>): Observable< HttpResponse<any>> | undefined  {

    const url = req.urlWithParams;
    // const cachedResponse = this.memoryget(req);

    // storageService.read wraps AsyncLocalStorage.getItem
    const readFromStorage$ = this.storagecache.getUnsafeItem<RequestCacheEntry>(url)
    .pipe(
      switchMap((x) => {
       if  (x === undefined || isNil(x) || x.lastRead < (Date.now() - maxAgeInLocalStorage))
        { return  of(undefined) ; } else { return   of(x.response); }
      } )
    );

       return readFromStorage$;
      //.pipe(switchMap((value) => (value !== undefined && !isNil(value) ) ? of(value) : readFromStorage$ ));
}


  put(req: HttpRequest<any>, response: HttpResponse<any>): void {
    const url = req.urlWithParams;
    console.log(`Caching response from "${url}" in LocalStorage.`);

    if (response.body) {
      const entry = JSON.parse(JSON.stringify({ url, response, lastRead: Date.now() }));
      this.memoryput(req, entry);
      this.storagecache.setItem(url, entry).subscribe(() => {
        console.log('response cached in LocalStorage [ok]');
      });
    }
    // remove expired cache entries
    const expired = Date.now() - maxAgeInLocalStorage;
    this.storagecache.keys().pipe(
      mergeMap((keys) => from(keys)),
      switchMap((key) =>  this.storagecache.getUnsafeItem<RequestCacheEntry>(key)),
      filter((item) => item.lastRead < expired), /* filter expired */
      mergeMap((item) => this.storagecache.removeItem(item.url))  /* Remove the item for each key */
    ).subscribe({ complete: () => {
       // we want to act only when all the operations are done */
      console.log('Done!');
    } });

    console.log(`LocalStorage cache size: ${this.storagecache.size}.`);
  }

  memoryget(req: HttpRequest<any>): HttpResponse<any> | undefined {
    const url = req.urlWithParams;
    const cached = this.memorycache.get(url);

    if (!cached) {
      return undefined;
    }

    const isExpired = cached.lastRead < (Date.now() - maxAgeInMemory);
    const expired = isExpired ? 'expired ' : '';
    console.log(`Found ${expired} cached response for "${url} in memory".`);
    return isExpired ? undefined : cached.response;
  }

  memoryput(req: HttpRequest<any>, response: HttpResponse<any>): void {
    const url = req.urlWithParams;
    console.log(`Caching response from "${url}" to memory.`);

    if (response.body) {
      console.log('response cached in memory[ok]');
      const entry = { url, response, lastRead: Date.now() };
      this.memorycache.set(url, entry);
    }
    // remove expired cache entries
    const expired = Date.now() - maxAgeInMemory;
    this.memorycache.forEach(entry => {
      if (entry.lastRead < expired) {
        this.memorycache.delete(entry.url);
      }
    });

    console.log(`Memory cache size: ${this.memorycache.size}.`);
  }

}
