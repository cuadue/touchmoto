package com.cuadue.touchmoto;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.Window;
import com.cuadue.touchmoto.TouchMotoView;
import com.cuadue.touchmoto.TouchMotoView.TouchMotoThread;

public class TouchMoto extends Activity {

	/** A handle to the thread that's actually running the animation. */
    private TouchMotoThread mMotoThread;

    /** A handle to the View in which the game is running. */
    private TouchMotoView mMotoView;

    /**
     * Invoked during init to give the Activity a chance to set up its Menu.
     * 
     * @param menu the Menu to which entries may be added
     * @return true
     */
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        super.onCreateOptionsMenu(menu);
        return true;
    }

    /**
     * Invoked when the user selects an item from the Menu.
     * 
     * @param item the Menu entry which was selected
     * @return true if the Menu item was legit (and we consumed it), false
     *         otherwise
     */
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        /*
    	switch (item.getItemId()) {
            case MENU_START:
                mLunarThread.doStart();
                return true;
            case MENU_STOP:
                mLunarThread.setState(LunarThread.STATE_LOSE,
                        getText(R.string.message_stopped));
        }
		*/
        return false;
    }

    /**
     * Invoked when the Activity is created.
     * 
     * @param savedInstanceState a Bundle containing state saved from a previous
     *        execution, or null if this is a new execution
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // turn off the window's title bar
        requestWindowFeature(Window.FEATURE_NO_TITLE);

        // tell system to use the layout defined in our XML file
        setContentView(R.layout.lunar_layout);

        // get handles to the LunarView from XML, and its LunarThread
        mMotoView = (TouchMotoView) findViewById(R.id.lunar);
        mMotoThread = mMotoView.getThread();

        // give the LunarView a handle to the TextView used for messages
        //mMotoView.setTextView((TextView) findViewById(R.id.text));
        mMotoView.setOnTouchListener(mMotoThread);
    }

    /**
     * Invoked when the Activity loses user focus.
     */
    @Override
    protected void onPause() {
        super.onPause();
        mMotoView.getThread().pause(); // pause game when Activity pauses
    }

    /**
     * Notification that something is about to happen, to give the Activity a
     * chance to save state.
     * 
     * @param outState a Bundle into which this Activity should save its state
     */
    @Override
    protected void onSaveInstanceState(Bundle outState) {
        // just have the View's thread save its state into our Bundle
        super.onSaveInstanceState(outState);
        // mMotoThread.saveState(outState);
        Log.w(this.getClass().getName(), "SIS called");
    }
}
