import { Injectable } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd, ActivatedRouteSnapshot, Params, PRIMARY_OUTLET } from '@angular/router';
import { Url2StatutePipe } from '../pipes/url2statute.pipe';

interface IRoutePart {
  title: string;
  breadcrumb: string;
  params?: Params;
  url: string;
  urlSegments: any[];
}

@Injectable()
export class RoutePartsService {
  private readonly regpattern = new RegExp('([^{]*?)(?=\})');
  public routeParts: IRoutePart[];
  constructor(private router: Router) {}

  ngOnInit() {
  }
  generateRouteParts(snapshot: ActivatedRouteSnapshot): IRoutePart[] {

    let routeParts = <IRoutePart[]>[];
    if (snapshot) {
      if (snapshot.firstChild) {
        routeParts = routeParts.concat(this.generateRouteParts(snapshot.firstChild));
      }
      if (snapshot.data['title'] && snapshot.url.length) {
        // console.log(snapshot.data['title'], snapshot.url)
        let title = snapshot.data['title'];
        let breadcrumb = snapshot.data['breadcrumb'];

        const matches = (title.match(this.regpattern) || []);
        if (matches.length > 0) {
          const param_name = matches[0].trim();
          const param_value = snapshot.params[param_name];
          if (param_value) {
            title = breadcrumb = new Url2StatutePipe().transform(param_value);
          }
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

}
