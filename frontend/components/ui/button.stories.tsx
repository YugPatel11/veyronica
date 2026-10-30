import { Button } from "./button";

const meta = {
  title: "UI/Button",
  component: Button,
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "destructive", "outline", "secondary", "ghost", "link", "glow"],
    },
    size: {
      control: "select",
      options: ["default", "sm", "lg", "icon"],
    },
    disabled: { control: "boolean" },
  },
};

export default meta;

export const Primary = {
  args: {
    children: "Primary Button",
    variant: "default",
  },
};

export const Secondary = {
  args: {
    children: "Secondary Button",
    variant: "secondary",
  },
};

export const Destructive = {
  args: {
    children: "Destructive Action",
    variant: "destructive",
  },
};

export const Glow = {
  args: {
    children: "Glowing Accent",
    variant: "glow",
  },
};
