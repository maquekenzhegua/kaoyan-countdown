package io.github.maquekenzhegua.kaoyan;

import android.os.Bundle;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        registerPlugin(ReminderPlugin.class);
    }

    @Override
    public void onResume() {
        super.onResume();
        ReminderScheduler.reschedule(this);
        CountdownWidgetProvider.updateAll(this);
    }
}
