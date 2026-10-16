import {Vector3} from './vendor/three.module.js';
const V=(x,y,z)=>new Vector3(x,y,z);
export const smooth=(a,b,u)=>a.clone().lerp(b,Math.max(0,Math.min(1,u))**2*(3-2*Math.max(0,Math.min(1,u))));
export const HOME=V(.45,2.2,1.6);
export const AGV_SUPPORT={deckTop:.75,palletOrigin:.81,palletTop:1.085,cartonCenter:1.305};
export function stackSlot(kind,id){return kind==='depallet'?V(-2.3+(id%2-.5)*.64,1.36+Math.floor(id/4)*.44,(Math.floor(id/2)%2-.5)*.58):V(2.1+(id%2-.5)*.64,1.21+Math.floor(id/4)*.44,1+(Math.floor(id/2)%2-.5)*.58);}
export function bufferSlot(kind,id){return kind==='depallet'?V(2.2+((7-id)%4-1.5)*.64,1.205,1.4+(Math.floor((7-id)/4)-.5)*.58):V(-2.7+(id%4-1.5)*.64,1.205,.3+(Math.floor(id/4)-.5)*.58);}
function route(points,u){const n=points.length-1,x=Math.max(0,Math.min(.999999999,u))*n,i=Math.floor(x);return smooth(points[i],points[i+1],x-i);}
export function transfer(A,B,p,lift=.5,frontZ=1.6){const a=A.clone().add(V(0,lift,0)),b=B.clone().add(V(0,lift,0));return route([A,a,V(A.x,a.y,frontZ),V(.45,Math.max(a.y,b.y),frontZ),V(B.x,b.y,frontZ),b,B],p);}
export function approach(A,p){const above=A.clone().add(V(0,.25,0));return route([HOME,V(A.x,Math.max(HOME.y,above.y),1.6),above,A],p);}
export function withdraw(A,p){const above=A.clone().add(V(0,.23,0));return route([A,above,V(A.x,Math.max(HOME.y,above.y),1.6),HOME],p);}
export function palletLoop(kind,raw){const t=((raw%240)+240)%240,turn=Math.floor(t/15),stage=Math.floor((t%15)/3),p=(t%3)/3,reverse=turn>=8,n=turn%8,id=kind==='depallet'?(reverse?n:7-n):(reverse?7-n:n),stack=stackSlot(kind,id),buffer=bufferSlot(kind,id),A=(kind==='depallet')!==reverse?stack:buffer,B=(kind==='depallet')!==reverse?buffer:stack,pick=A.clone().add(V(0,.34,0)),place=B.clone().add(V(0,.34,0));const positions=Array.from({length:8},(_,j)=>{let atStack;if(kind==='depallet')atStack=reverse?j<id:j<=id;else atStack=reverse?j<=id:j<id;return atStack?stackSlot(kind,j):bufferSlot(kind,j);});let target=HOME.clone();if(stage===2)target=approach(pick,p);if(stage===3){target=transfer(pick,place,p);positions[id]=target.clone().add(V(0,-.34,0));}else positions[id]=(stage===4?B:A).clone();if(stage===4)target=withdraw(place,p);return {stage,p,id,positions,target,pick,place,reverse,held:stage===3};}
export const CNC={A:V(-2.5,1.22,.1),B:V(.25,1.405,2.35),C:V(2.5,1.17,.1),front:V(.25,1.65,1.0),offset:.245,walls:[[-1.2,1.35,2.6,.12,2.7,2.4],[1.7,1.35,2.6,.12,2.7,2.4],[.25,1.35,3.85,3.02,2.7,.12],[.25,2.72,2.6,3.02,.12,2.6],[-1.3,2.2,1.34,.06,4.4,.06],[1.8,2.2,1.34,.06,4.4,.06],[.25,4.4,1.34,3.16,.08,.08]]};
const CNC_HOME=V(.25,2.05,.25);
export function cncMotion(raw){const t=((raw%15)+15)%15,stage=Math.floor(t/3),p=(t%3)/3,{A,B,C,offset}=CNC,pick=A.clone().add(V(0,offset,0)),place=B.clone().add(V(0,offset,0)),out=C.clone().add(V(0,offset,0)),front=V(.25,place.y,1);let target=CNC_HOME.clone(),part=A.clone(),held=false,open=1;
 if(stage===0){target=transfer(out,pick,p,.25,.4);part=target.clone().add(V(0,-offset,0));held=true;}
 if(stage===1){const above=pick.clone().add(V(0,.25,0));target=p<.25?smooth(pick,above,p/.25):p<.5?smooth(above,CNC_HOME,(p-.25)/.25):p<.75?smooth(CNC_HOME,above,(p-.5)/.25):smooth(above,pick,(p-.75)/.25);}
 if(stage===2){const lift=pick.clone().add(V(0,.25,0));target=p<.2?smooth(pick,lift,p/.2):p<.65?smooth(lift,front,(p-.2)/.45):smooth(front,place,(p-.65)/.35);part=target.clone().add(V(0,-offset,0));held=true;}
 if(stage===3){part=B.clone();target=p<.35?smooth(place,front,p/.35):p<.6?smooth(front,CNC_HOME,(p-.35)/.25):CNC_HOME.clone();open=1-Math.max(0,Math.min(1,(p-.67)/.18));}
 if(stage===4){open=Math.min(1,p/.12);part=B.clone();if(p<.15)target=CNC_HOME.clone();else if(p<.35)target=smooth(CNC_HOME,front,(p-.15)/.2);else if(p<.5)target=smooth(front,place,(p-.35)/.15);else{const u=(p-.5)/.5;target=u<.3?smooth(place,front,u/.3):route([front,V(out.x,front.y,.4),out],(u-.3)/.7);part=target.clone().add(V(0,-offset,0));held=true;}}
 return {stage,p,target,part,held,doorOpen:open,pick,place,front};}
