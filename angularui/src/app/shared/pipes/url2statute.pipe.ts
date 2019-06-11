import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'url2statute' })
export class Url2StatutePipe implements PipeTransform {
  transform(statuteID: string) {

    // tslint:disable-next-line:curly
    if (statuteID === null)
      return '';

      const parts  = statuteID.split('_');
      return this.fnStatuteName(...parts);

  }

fnStatuteName(type?: string, name?: string, year?: string) {
    const lookup = {
        'l': 'Ν',
        'pd': 'Π.Δ',
         '': '??',
      };
    type = lookup[type] || '' ;
    return `${type}. ${name}/${year}`;
}

}
