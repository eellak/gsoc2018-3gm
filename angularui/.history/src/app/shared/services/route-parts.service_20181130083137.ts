import { Injectable } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd, ActivatedRouteSnapshot, Params, PRIMARY_OUTLET } from "@angular/router";

interface IRoutePart {
  title: string,
  breadcrumb: string,
  params?: Params,
  url: string,
  urlSegments: any[]
}

@Injectable()
export class RoutePartsService {
  public routeParts: IRoutePart[];
  constructor(private router: Router) {}

  ngOnInit() {
  }
  generateRouteParts(snapshot: ActivatedRouteSnapshot): IRoutePart[] {
   

    var routeParts = <IRoutePart[]>[];
    if (snapshot) {
      if (snapshot.firstChild) {
        routeParts = routeParts.concat(this.generateRouteParts(snapshot.firstChild));
      }
      if (snapshot.data['title'] && snapshot.url.length) {
        // console.log(snapshot.data['title'], snapshot.url)
        let title = snapshot.data['title'];
        let breadcrumb = snapshot.data['breadcrumb'];

        const regpattern = new RegExp('([^{]*?)(?=\})');
        const matches = (title.match(regpattern) || []);
        if (matches.length > 0) {
          const param_value = snapshot.params[matches[0].trim()];
          const statute_parts  = param_value.split('_');
          title = breadcrumb  = this.fnStatuteName(...statute_parts);

        }

        routeParts.push({
          title: title,
          breadcrumb: breadcrumb ,
          url: snapshot.url[0].path,
          urlSegments: snapshot.url,
          params: snapshot.params
        });
      }
    }
    return routeParts;
  }

  fnStatuteName(type?: string, name?: string, year?: string) {
    const lookup = {
        'l': 'Ν',
        'pd': 'Π.Δ',
         '': '??',
      };
    type = lookup[type];
    return `${type}. ${name}/${year}`;

}

}