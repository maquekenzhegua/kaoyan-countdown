package io.github.maquekenzhegua.kaoyan;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** 开机后重新安排每日提醒并刷新小组件。 */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        ReminderScheduler.reschedule(context);
        CountdownWidgetProvider.updateAll(context);
    }
}
