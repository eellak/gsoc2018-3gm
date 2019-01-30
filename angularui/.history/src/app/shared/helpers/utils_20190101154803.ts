export function getIndexBy(array: Array<{}>, { name, value }): number {
  for (let i = 0; i < array.length; i++) {
    if (array[i][name] === value) {
      return i;
    }
  }
  return -1;
}

export function isUndefined (value: any): value is undefined {
  
  return typeof value === 'undefined';
}

export function isNull (value: any): value is null {
  
  return value === null;
}

export function isNilOrEmpty(value:any):boolean {
return isNil(value) || (isString(value) && value.length===0);
}

export function isNumber (value: any): value is number {
  
  return typeof value === 'number';
}

export function isNumberFinite (value: any): value is number {
  
  return isNumber(value) && isFinite(value);
}

// Not strict positive
export function isPositive (value: number): boolean {
  
  return value >= 0;
}


export function isInteger (value: number): boolean {
  
  // No rest, is an integer
  return (value % 1) === 0;
}

export function isNil (value: any): value is (null|undefined) {
  return value === null || typeof (value) === 'undefined';
}

export function isString (value: any): value is string {
  
  return typeof value === 'string';
}

export function isObject (value: any): boolean {
  
  return value !== null && typeof value === 'object';
}

export function isArray (value: any): boolean {
  
  return Array.isArray(value);
}

export function isFunction (value: any): boolean {
  
  return typeof value === 'function';
}

export function toDecimal (value: number, decimal: number): number {
  
  return Math.round(value * Math.pow(10, decimal)) / Math.pow(10, decimal);
}

export function upperFirst (value: string): string {
  
  return value.slice(0, 1).toUpperCase() + value.slice(1);
}

export function createRound (method: string): Function {
  
  // <any>Math to suppress error
  const func: any = (<any>Math)[method];
  return function (value: number, precision: number = 0) {
    
    if (typeof value === 'string') {
      throw new TypeError('Rounding method needs a number');
    }
    
    if (typeof precision !== 'number' || isNaN(precision)) {
      precision = 0;
    }
    
    if (precision) {
      
      let pair = `${value}e`.split('e');
      const val = func( `${pair[0]}e` + (+pair[1] + precision));
      
      pair = `${val}e`.split('e');
      return +(pair[0] + 'e' + (+pair[1] - precision));
    }
    
    return func(value);
  };
}

export function leftPad (str: string, len: number = 0, ch: any = ' ') {
  
  str = String(str);
  ch = toString(ch);
  let i = -1;
  const length = len - str.length;
  
  while (++i < length && (str.length + ch.length) <= len) {
    str = ch + str;
  }
  
  return str;
}

export function rightPad (str: string, len: number = 0, ch: any = ' ') {
  
  str = String(str);
  ch = toString(ch);
  
  let i = -1;
  const length = len - str.length;
  
  while (++i < length && (str.length + ch.length) <= len) {
    str += ch;
  }
  
  return str;
}

export function toString (value: number|string) {
  
  return `${value}`;
}

export function pad (str: string, len: number = 0, ch: any = ' '): string{
  
  str = String(str);
  ch = toString(ch);
  let i = -1;
  const length = len - str.length;
  
  
  let left = true;
  while (++i < length) {
    
    const l = (str.length + ch.length <= len) ? (str.length + ch.length) : (str.length + 1);
    
    if (left) {
      str = leftPad(str, l, ch);
    }
    else {
      str = rightPad(str, l, ch);
    }
    
    left = !left;
  }
  
  return str;
}

export function flatten (input: any[], index: number = 0): any[] {
  
  if (index >= input.length) {
    return input;
  }
  
  if (isArray(input[index])) {
    return flatten(
    input.slice(0, index).concat(input[index], input.slice(index + 1)),
    index
    );
  }
  
  return flatten(input, index + 1);
  
}


export function getProperty (value: { [key: string]: any}, key: string): any {
  
  if (isNil(value) || !isObject(value)) {
    return undefined;
  }
  
  const keys: string[] = key.split('.');
  let result: any = value[keys.shift()!];
  
  for (const key of keys) {
    if (isNil(result) || !isObject(result)) {
      return undefined;
    }
    
    result = result[key];
  }
  
  return result;
}
