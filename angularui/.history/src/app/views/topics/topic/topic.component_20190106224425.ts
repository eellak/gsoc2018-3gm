import { Component,  Input } from '@angular/core';
import { Topic } from '@app/shared/models/legal.models';
import { isNilOrEmpty } from '@app/shared/helpers/utils';



@Component({
  selector: 'app-topic',
  templateUrl: './topic.component.html',
  styleUrls: ['./topic.component.scss'],

})
export class TopicComponent{
  @Input() topic: Topic;


  constructor(
  ) { }
  
isSelected(item:string):boolean{
    return (!isNilOrEmpty(item) && item.startsWith('ν'))
}

}
