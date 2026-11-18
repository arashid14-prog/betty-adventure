import tkinter as tk
import math
import os
import time

W, H = 960, 540
WORLD_W = 3600
GROUND_Y = 460

class Skybound:
    def __init__(self, root):
        self.root = root
        root.title('Betty Adventure')
        root.resizable(False, False)
        self.cv = tk.Canvas(root, width=W, height=H, highlightthickness=0, bg='#079fe8')
        self.cv.pack()
        assets = os.path.join(os.path.dirname(__file__), 'assets')
        self.cat_idle = tk.PhotoImage(file=os.path.join(assets, 'cat_idle.png')).zoom(3, 3)
        self.cat_run = [tk.PhotoImage(file=os.path.join(assets, f'cat_run{i}.png')).zoom(3, 3) for i in range(1, 5)]
        self.cat_jump = tk.PhotoImage(file=os.path.join(assets, 'cat_jump.png')).zoom(3, 3)
        self.cat_idle_left = tk.PhotoImage(file=os.path.join(assets, 'cat_idle_left.png')).zoom(3, 3)
        self.cat_run_left = [tk.PhotoImage(file=os.path.join(assets, f'cat_run{i}_left.png')).zoom(3, 3) for i in range(1, 5)]
        self.cat_jump_left = tk.PhotoImage(file=os.path.join(assets, 'cat_jump_left.png')).zoom(3, 3)
        self.slime = tk.PhotoImage(file=os.path.join(assets, 'slime.png')).subsample(3, 3)
        self.keys = set()
        root.bind('<KeyPress>', self.key_down)
        root.bind('<KeyRelease>', self.key_up)
        self.platforms = [(0,GROUND_Y,540,80),(610,GROUND_Y,440,80),(1120,GROUND_Y,560,80),(1760,GROUND_Y,460,80),(2300,GROUND_Y,560,80),(2950,GROUND_Y,650,80),
          (245,370,120,20),(430,310,120,20),(720,365,130,20),(910,300,120,20),(1240,370,150,20),(1450,305,140,20),(1850,360,130,20),(2040,295,120,20),(2400,365,140,20),(2620,305,130,20),(3090,370,150,20),(3330,300,130,20)]
        self.coins = [(x,y) for x,y in [(280,338),(465,278),(765,333),(950,268),(1290,338),(1500,273),(1890,328),(2080,263),(2440,333),(2660,273),(3130,338),(3370,268)]]
        self.enemies = [{'x':x,'start':x,'dir':1,'alive':True,'range':r} for x,r in [(500,55),(1010,70),(1580,55),(2140,55),(2790,70),(3260,45)]]
        self.px,self.py=70,GROUND_Y-42
        self.vx=self.vy=0; self.grounded=False; self.camera=0; self.got=set(); self.lives=3; self.state='title'; self.blink=0; self.facing=1
        root.bind('<KeyPress>', self.key_down)
        root.bind('<KeyRelease>', self.key_up)
        self.draw()
        root.after(16,self.loop)

    def key_down(self,e):
        k=e.keysym.lower(); self.keys.add(k)
        if k in ('space','up','w') and self.state=='play' and self.grounded: self.vy=-12.2; self.grounded=False
        if k in ('return','space') and self.state in ('title','win','dead'): self.restart()

    def key_up(self,e): self.keys.discard(e.keysym.lower())

    def restart(self):
        self.px,self.py=70,GROUND_Y-42; self.vx=self.vy=0; self.camera=0; self.got.clear(); self.lives=3; self.facing=1
        for e in self.enemies: e.update(x=e['start'],dir=1,alive=True)
        self.state='play'

    def loop(self):
        self.blink+=1
        if self.state=='play': self.update()
        self.draw(); self.root.after(16,self.loop)

    def update(self):
        left=any(k in self.keys for k in ('left','a')); right=any(k in self.keys for k in ('right','d'))
        self.vx=(4.1 if right else 0)-(4.1 if left else 0)
        if self.vx: self.facing=1 if self.vx>0 else -1
        oldbottom=self.py+20
        self.px=max(15,min(WORLD_W-15,self.px+self.vx)); self.vy=min(14,self.vy+0.58); self.py+=self.vy; self.grounded=False
        for x,y,w,h in self.platforms:
            if self.px+14>x and self.px-14<x+w and oldbottom<=y and self.py+20>=y and self.vy>=0:
                self.py=y-20; self.vy=0; self.grounded=True
        if self.py>H+40: self.hurt()
        for i,(x,y) in enumerate(self.coins):
            if i not in self.got and math.hypot(self.px-x,self.py-y)<30: self.got.add(i)
        for e in self.enemies:
            if not e['alive']: continue
            e['x']+=1.25*e['dir']
            if abs(e['x']-e['start'])>e['range']: e['dir']*=-1
            if abs(self.px-e['x'])<29 and abs(self.py-(GROUND_Y-20))<28:
                if self.vy>2 and self.py<GROUND_Y-27: e['alive']=False; self.vy=-8
                else: self.hurt()
        self.camera=max(0,min(WORLD_W-W,self.px-W*.38))
        if self.px>3510 and len(self.got)>=8: self.state='win'

    def hurt(self):
        self.lives-=1
        if self.lives<=0: self.state='dead'
        else: self.px=max(70,self.px-150); self.py=GROUND_Y-42; self.vx=self.vy=0

    def rect(self,x1,y1,x2,y2,fill,outline=''):
        self.cv.create_rectangle(x1,y1,x2,y2,fill=fill,outline=outline)

    def text(self,x,y,s,size,fill='#fff',**kw):
        self.cv.create_text(x,y,text=s,font=('Arial',size,'bold'),fill=fill,**kw)

    def draw(self):
        c=self.cv; c.delete('all'); cam=self.camera
        # Layered sky and distant green hills.
        self.rect(0,0,W,H,'#83d8f2')
        for i in range(8):
            x=(i*190-cam*.18)%(W+220)-100
            c.create_oval(x,80,x+90,112,fill='#d8f4fa',outline='')
            c.create_oval(x+25,65,x+125,112,fill='#d8f4fa',outline='')
        for i in range(-1,8):
            x=i*230-(cam*.34%230)
            c.create_polygon(x,GROUND_Y,x+110,245,x+260,GROUND_Y,fill='#62bd9b',outline='')
            c.create_polygon(x+90,GROUND_Y,x+210,285,x+340,GROUND_Y,fill='#51ab91',outline='')
        # Ground and floating platforms.
        for x,y,w,h in self.platforms:
            sx=x-cam
            if sx+w<0 or sx>W: continue
            self.rect(sx,y,sx+w,y+h,'#9b5b38')
            self.rect(sx,y,sx+w,y+10,'#48b85b')
            for bx in range(int(sx+15),int(sx+w-5),32):
                self.rect(bx,y+24,bx+3,y+38,'#79432f')        # Coins
        for i,(x,y) in enumerate(self.coins):
            if i in self.got: continue
            sx=x-cam
            if -20<sx<W+20:
                c.create_oval(sx-10,y-13,sx+10,y+13,fill='#ffd34e',outline='#e79c2d',width=3)
                self.rect(sx-2,y-8,sx+2,y+8,'#fff1a1')
        # Green slime enemies
        for e in self.enemies:
            if e['alive'] and -40<e['x']-cam<W+40:
                sx=e['x']-cam; y=GROUND_Y-19
                c.create_image(sx,y-1,image=self.slime)
        # Little cat house at the end of the trail; the doorway is the goal.
        hx=3440-cam
        c.create_polygon(hx-12,GROUND_Y-82,hx+68,GROUND_Y-145,hx+148,GROUND_Y-82,fill='#c95f4b',outline='#873e3b',width=4)
        c.create_rectangle(hx,GROUND_Y-84,hx+136,GROUND_Y,fill='#f0c988',outline='#9a6349',width=3)
        c.create_rectangle(hx+52,GROUND_Y-58,hx+92,GROUND_Y,fill='#573b38',outline='#704635',width=3)
        c.create_oval(hx+80,GROUND_Y-33,hx+86,GROUND_Y-27,fill='#ffd76a',outline='')
        c.create_rectangle(hx+17,GROUND_Y-65,hx+42,GROUND_Y-42,fill='#bce9f0',outline='#9a6349',width=2)
        c.create_line(hx+29,GROUND_Y-65,hx+29,GROUND_Y-42,fill='#9a6349',width=2)
        c.create_line(hx+17,GROUND_Y-53,hx+42,GROUND_Y-53,fill='#9a6349',width=2)
        c.create_text(hx+68,GROUND_Y-99,text='HOME',font=('Arial',10,'bold'),fill='#fff2cf')        # Animated pixel-cat hero, aligned above the collision feet
        px=self.px-cam; py=self.py
        if not self.grounded:
            sprite=self.cat_jump if self.facing>0 else self.cat_jump_left
        elif abs(self.vx)>0:
            frame=(self.blink//7)%len(self.cat_run)
            sprite=self.cat_run[frame] if self.facing>0 else self.cat_run_left[frame]
        else:
            sprite=self.cat_idle if self.facing>0 else self.cat_idle_left
        c.create_image(px,py-13,image=sprite)
        # HUD
        self.rect(0,0,W,56,'#172b48')
        self.text(20,27,'BETTY ADVENTURE',18,'#ffe276',anchor='w')
        self.text(255,27,f'COINS  {len(self.got)}/{len(self.coins)}',14,'white',anchor='w')
        self.text(435,27,'♥ '*self.lives,16,'#ff7379',anchor='w')
        self.text(W-18,27,'A / D or ← / →   move     SPACE / ↑ jump',12,'#d7e8ff',anchor='e')
        if self.state=='title':
            self.rect(0,0,W,H,'#102343')
            self.text(W/2,125,'BETTY ADVENTURE',48,'#ffe276')
            self.text(W/2,184,'A little platform adventure',20,'#c5e9ff')
            self.text(W/2,270,'Collect 8 coins, dodge the green slimes,',20,'white')
            self.text(W/2,301,'and head into the little cat house!',20,'white')
            self.text(W/2,383,'ARROWS / A D  MOVE     SPACE / ↑  JUMP',17,'#ffe276')
            self.text(W/2,445,'PRESS ENTER TO PLAY',19,'white')
        elif self.state in ('win','dead'):
            self.rect(0,0,W,H,'#102343')
            if self.state=='win': self.text(W/2,190,'YOU MADE IT HOME!',42,'#ffe276')
            else: self.text(W/2,190,'TRY AGAIN',42,'#ff8989')
            self.text(W/2,260,f'Coins collected: {len(self.got)} / {len(self.coins)}',21,'white')
            self.text(W/2,355,'PRESS ENTER TO PLAY AGAIN',18,'#c5e9ff')

if __name__=='__main__':
    root=tk.Tk(); game=Skybound(root); root.mainloop()





