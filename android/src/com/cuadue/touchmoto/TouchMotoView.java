package com.cuadue.touchmoto;

import android.content.Context;
import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.drawable.Drawable;
import android.os.Handler;
import android.os.Message;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.widget.TextView;
import java.util.ArrayList;

class TouchMotoView extends SurfaceView implements SurfaceHolder.Callback {
   
    class TouchMotoThread extends Thread implements OnTouchListener {
        public Rider player;
        private long mLastTime;
        private boolean mRun = false;
        private SurfaceHolder mSurfaceHolder; //this is what is synchronized between threads
        private Bitmap mBackgroundImage;
        private ArrayList<Sprite> sprites = new ArrayList<Sprite>();
        private int canvasHeight = 0;

        public TouchMotoThread(SurfaceHolder surfaceHolder, Context context, Handler handler) {
            mSurfaceHolder = surfaceHolder;
            Resources res = context.getResources();
            
            // load background image as a Bitmap instead of a Drawable b/c
            // we don't need to transform it and it's faster to draw this way
            mBackgroundImage = BitmapFactory.decodeResource(res, R.drawable.earthrise);
            Drawable d = res.getDrawable(R.drawable.lander_plain);
            player = new Rider(d);
            
            d = res.getDrawable(R.drawable.lander_plain);
            player.target = new Target(d);
            sprites.add(player);
            sprites.add(player.target);
        }
        

        public boolean onTouch(View v, MotionEvent event){
            player.target.visible = true;
        	player.target.x = event.getX();
        	player.target.y = event.getY();
        	return true;
        }

        /* Callback invoked when the surface dimensions change. */
        public void setSurfaceSize(int width, int height) {
            canvasHeight = height;
            // synchronized to make sure these all change atomically
            synchronized (mSurfaceHolder) {
                mBackgroundImage = Bitmap.createScaledBitmap(mBackgroundImage, width, height, true);
            }
        }
        
        @Override
        public void run() {
            while (mRun) {
                Canvas c = null;
                try {
                    c = mSurfaceHolder.lockCanvas(null);
                    synchronized (mSurfaceHolder) {
                        updatePhysics();
                        doDraw(c);
                    }
                } finally {
                    if (c != null) {
                        mSurfaceHolder.unlockCanvasAndPost(c);
                    }
                }
            }
        }
        
        public void setRunning(boolean b) {
            mRun = b;
        }

        public void pause() {
            this.suspend();
        }
        
        public void unpause() {
            // Move the real time clock up to now
            synchronized (mSurfaceHolder) {
                mLastTime = System.currentTimeMillis() + 100;
            }
            this.resume();
        }

        /**
         * Draws the ship, fuel/speed bars, and background to the provided
         * Canvas.
         */
        private void doDraw(Canvas canvas) {
            // Draw the background image. Operations on the Canvas accumulate
            // so this is like clearing the screen.
        	canvas.drawBitmap(mBackgroundImage, 0, 0, null);
            
            float r = (float)player.turningRadius();
            if(r < 1000 && r > 0){
                double tmp = player.angle + (player.psi_sign * Math.PI/2f);
                float centerx = (int)(player.x + r * Math.cos(tmp));
                float centery = (int)(player.y + r * Math.sin(tmp));
                Paint p = new Paint();
                p.setARGB(255, 255, 0, 0);
                p.setStyle(Paint.Style.STROKE);
                p.setStrokeWidth(2);
                canvas.drawCircle(centerx, centery, r, p);
            }
            
        	for(int i = 0; i < sprites.size(); i++){
        		sprites.get(i).draw(canvas);
        	}
        }
        
        private void updatePhysics() {
            long now = System.currentTimeMillis();
            if (mLastTime > now) return;
            double dt = (now - mLastTime) / 1000.0;

        	for(int i = 0; i < sprites.size(); i++){
        		sprites.get(i).update(dt);
        	}
        	
        	mLastTime = now;
        }
    }

    /** Pointer to the text view to display "Paused.." etc. */
    private TextView mStatusText;

    /** The thread that actually draws the animation */
    private TouchMotoThread thread;
    
    public TouchMotoView(Context context, AttributeSet attrs, int defStyle){
    	this(context, attrs);
    }
    
    public TouchMotoView(Context context) {
    	this(context, null);
    }

    public TouchMotoView(Context context, AttributeSet attrs) {
        super(context, attrs);

        // register our interest in hearing about changes to our surface
        SurfaceHolder holder = getHolder();
        holder.addCallback(this);

        // create thread only; it's started in surfaceCreated()
        thread = new TouchMotoThread(holder, context, new Handler() {
            @Override
            public void handleMessage(Message m) {
                mStatusText.setVisibility(m.getData().getInt("viz"));
                mStatusText.setText(m.getData().getString("text"));
            }
        });

        setFocusable(true); // make sure we get key events
    }

    public TouchMotoThread getThread() {
        return thread;
    }

    /**
     * Standard window-focus override. Notice focus lost so we can pause on
     * focus lost. e.g. user switches to take a call.
     */
    @Override
    public void onWindowFocusChanged(boolean hasWindowFocus) {
        if (!hasWindowFocus) 
        	thread.pause();
        else
        	thread.unpause();
    }

    public void setTextView(TextView textView) {
        mStatusText = textView;
    }

    /* Callback invoked when the surface dimensions change. */
    public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) {
        thread.setSurfaceSize(width, height);
    }

    public void surfaceCreated(SurfaceHolder holder) {
        // start the thread here so that we don't busy-wait in run()
        // waiting for the surface to be created
        thread.setRunning(true);
        thread.start();
    }

    /*
     * Callback invoked when the Surface has been destroyed and must no longer
     * be touched. WARNING: after this method returns, the Surface/Canvas must
     * never be touched again!
     */
    public void surfaceDestroyed(SurfaceHolder holder) {
        // we have to tell thread to shut down & wait for it to finish, or else
        // it might touch the Surface after we return and explode
        boolean retry = true;
        thread.setRunning(false);
        while (retry) {
            try {
                thread.join();
                retry = false;
            } catch (InterruptedException e) {
            }
        }
    }
    
}
