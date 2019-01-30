import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'statute2url' })
export class Statute2UrlPipe implements PipeTransform {
  transform(statuteName: string) {

    // tslint:disable-next-line:curly
    if (statuteName === null)
      return '';

      // TODO : reverse engineer Python implementation
      statuteName = statuteName.replace('/', ' ');
      statuteName = statuteName.replace(new RegExp(`(?:\\s+)(?:tags)`, 'g'), $1 => ` ${$1.trim()}`);
      const parts  = statuteName.split(' ');
      return this.fnStatuteUrl(...parts);

  }

fnStatuteUrl(type?: string, name?: string, year?: string) {
    const re = /\./gi;
    const lookup = {
        'Ν': 'l',
        'ν': 'l',
        'ΠΔ': 'pd',
        'πδ': 'pd',
         '??': '',
      };
    type = lookup[type.replace(re, '')] || '' ;
    return `${type}_${name}_${year}`;
}

}
