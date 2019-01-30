import { Component, OnInit , OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { StatuteService } from '../statute.service';
import { Subscription , Observable } from 'rxjs';
import {
  VisEdges,
  VisNetworkData,
  VisNetworkOptions,
  VisNetworkService,
  VisNode,
  VisNodes,
  VisEdge} from 'ngx-vis';
import { StatuteLinks } from '@app/shared/models/legal.models';
import { AppLoaderService } from '@app/shared/services/app-loader/app-loader.service';
import { MatSnackBar } from '@angular/material';
import { finalize } from 'rxjs/operators';

  class ExampleNetworkData implements VisNetworkData {
    public nodes: VisNodes;
    public edges: VisEdges;
}

@Component({
  selector: 'app-statute-references',
  templateUrl: './statute-references.component.html',
  styleUrls: ['./statute-references.component.scss']
})
export class StatuteReferencesComponent implements OnInit, OnDestroy {

    public statuteID: string;
    public getLinksSub: Subscription;
    public links: StatuteLinks ;

    public visNetwork: string = 'networkId1';
    public visNetworkData: ExampleNetworkData;
    public visNetworkOptions: VisNetworkOptions;

  constructor(
      private route: ActivatedRoute,
      private statuteService: StatuteService,
      private visNetworkService: VisNetworkService,
      private snack: MatSnackBar,
      private loader: AppLoaderService,
      ) { }

  public networkInitialized(): void {
    // now we can use the service to register on events
    this.visNetworkService.on(this.visNetwork, 'click');
    this.visNetworkService.once(this.visNetwork,'beforeDrawing');
    this.visNetworkService.once(this.visNetwork,'afterDrawing');

    // open your console/dev tools to see the click params
    this.visNetworkService.click
        .subscribe((eventData: any[]) => {
            if (eventData[0] === this.visNetwork) {
              console.log(eventData[1]);
              const data = eventData[1].nodes;
              console.log(data);
            }
        });

        this.visNetworkService.beforeDrawing
        .subscribe( () => 
        {
          this.visNetworkService.moveTo(this.visNetwork , 
            {   scale:6  });
        }); //end subscribe

        this.visNetworkService.afterDrawing
        .subscribe( () => {
          this.visNetworkService.fit(this.visNetwork , {
            animation:  {
            duration: 2000,
            easingFunction: 'easeOutQuint'
           }
        }); // end fit
        }); // end subscribe

}

  ngOnInit() {
    this.statuteID = this.route.parent.snapshot.params['id'];
    this.getLinks();

  }

  getLinks() {
    setTimeout(() => {
      this.loader.open();
    });

    this.getLinksSub =  this.statuteService.getLinks(this.statuteID)
    .pipe(
      finalize(() =>  {
      this.loader.close();
    })
    )
    .subscribe(data => {
      this.links = data;
      this.loadLinksToNetwork();
    }
    ,
    err => {
    this.snack.open('Πρόβλημα κατά την ανάκτηση δεδομένων!', 'OK', { duration: 4000 });
    }
    ); //end subscribe
  }

  loadLinksToNetwork() {
    const item_per_level = 4;
    let level = 0;

    let root_node: VisNode = { 'id': this.statuteID , 'label': this.statuteID , 'title': this.statuteID, group: 'root', fixed: true };
    let incoming_nodes =  this.links.incoming;
    let outgoing_nodes = this.links.outgoing;

    let network_nodes: VisNode[] = [];
    let network_edges: VisEdge[] = [];

    // tslint:disable-next-line:forin
    for (const key in incoming_nodes) {
         const value = incoming_nodes[key];

         if (!value.toString().includes('τροποποιητικός'))  continue;
         const tooltip = value.map( val =>  'τροποποιείται ' + val[1]).join('</br>');

         if (network_nodes.length % item_per_level === 0) level++;


         const node: VisNode =  { 'id': key , 'label': key , 'title': tooltip ,  group: 'incoming' , level: level};
         network_nodes.push(node);

         const edge: VisEdge = {  from: key , to: this.statuteID  };
         network_edges.push(edge);
  }

  level++;
  root_node['level'] = level;
  network_nodes.push(root_node);
  level++;
    // tslint:disable-next-line:forin
    for (const key in outgoing_nodes) {
      const value = outgoing_nodes[key];
      const tooltip = value.map( val =>  val[0] + ' ' + val[1]).join('\n');
      const color = value.toString().includes('διαγράφεται') ? 'red' : 'lime';
      const node: VisNode =  { 'id': key , 'label': key , 'title': tooltip , color: color ,  group: 'outgoing' , level:level};
      network_nodes.push(node);

      const edge: VisEdge = {  from: this.statuteID, to: key , color: color  };
      network_edges.push(edge);

      if (network_nodes.length % item_per_level === 0) level++;
}


    // tslint:disable-next-line:max-line-length
    // const incoming_nodes: VisNode[] =  this.links.incoming[]
    // // this.links.incoming.filter(x => x.rel === 'τροποποιητικός').map( obj => ({ 'id': obj.statute , 'label': obj.statute , 'title': obj.statute}) );
    // const outgoing_nodes: VisNode[] = this.links.outgoing.map( obj => ({ 'id': obj.statute , 'label': obj.statute , 'title': obj.statute}) );
    // const routeNode: VisNode = { 'id': this.statuteID , 'label': this.statuteID , 'title': this.statuteID , color: 'lime' ,  shape: 'diamond' };
    // const nodes = new VisNodes([ routeNode , ...incoming_nodes, ...outgoing_nodes]);

    // const incoming_edges: VisEdge[] = this.links.incoming.map( obj => ({ from: obj.statute , to: this.statuteID  ,  arrows:'to' , dashes:true }) );
    // const outgoing_edges: VisEdge[] = this.links.outgoing.map( obj => ({ from: this.statuteID  , to: obj.statute ,  arrows:'to' , dashes:false }) );

    const nodes = new VisNodes(network_nodes);
    const edges = new VisEdges(network_edges);

    this.visNetworkData = {
      nodes,
      edges,
     };

     this.visNetworkOptions = {
      groups: {
        incoming: {
          shape: 'circle',
          color: {
            border: 'black',
            background: 'white',
            highlight: {
              border: 'yellow',
              background: 'orange'
            }
          },
          fontColor: 'red',
          fontSize: 18
        },
        outgoing: {
          shape: 'circle',
          color: {
            border: 'black',
            background: 'cyan',
            highlight: {
              border: 'yellow',
              background: 'red'
            }
          },
          fontColor: 'red',
          fontSize: 18
        },
        root: {
          shape: 'circle',
          size:40,
          color: {
            border: 'black',
            background: 'lime',
            highlight: {
              border: 'yellow',
              background: 'red'
            }
          },
          fontColor: 'red',
          fontSize: 18
        },
        // add more groups here
      },
        edges: {
            smooth: {
              enabled: true,
                type: 'cubicBezier',
                forceDirection: 'horizontal',
                roundness: 0.4
            },
            arrows: {
              to: { enabled: true, scaleFactor: 0.5 },
              middle: { enabled: false, scaleFactor: 1 },
              from: { enabled: false, scaleFactor: 0.5 }
            },
            color : {
              inherit: false
            }
        },
        layout: {
            hierarchical: {
                direction: 'LR'
            }
        },
        physics: false
    };

  }


  public ngOnDestroy(): void {
    this.visNetworkService.off(this.visNetwork, 'click');
    if (this.getLinksSub) {
        this.getLinksSub.unsubscribe();
      }
}

}
